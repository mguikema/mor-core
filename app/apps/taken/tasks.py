import celery
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db import OperationalError, transaction

logger = get_task_logger(__name__)

DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6
RETRY_BACKOFF_MAX = 60 * 30
RETRY_BACKOFF = 120


class BaseTaskWithRetry(celery.Task):
    autoretry_for = (Exception,)
    max_retries = MAX_RETRIES
    default_retry_delay = DEFAULT_RETRY_DELAY
    retry_backoff_max = RETRY_BACKOFF_MAX
    retry_backoff = RETRY_BACKOFF
    retry_jitter = True


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_taak_aanmaken(self, taakgebeurtenis_id):
    from apps.applicaties.models import Applicatie
    from apps.meldingen.managers import MeldingManager
    from apps.taken.models import Taakgebeurtenis, Taakopdracht

    with transaction.atomic():
        try:
            taakgebeurtenis = (
                Taakgebeurtenis.objects.using(settings.DEFAULT_DATABASE_KEY)
                .select_for_update(nowait=True)
                .get(id=taakgebeurtenis_id)
            )
        except OperationalError:
            raise MeldingManager.TaakgebeurtenisInGebruik(
                "De taakgebeurtenis is op dit moment in gebruik, probeer het later nog eens."
            )

        try:
            taakopdracht = (
                Taakopdracht.objects.using(settings.DEFAULT_DATABASE_KEY)
                .select_for_update(nowait=True)
                .get(id=taakgebeurtenis.taakopdracht.id)
            )
        except OperationalError:
            raise MeldingManager.TaakopdrachtInGebruik(
                "De taakopdracht is op dit moment in gebruik, probeer het later nog eens."
            )

        if taakopdracht.taak_url:
            return f"Taak is al aangemaakt bij {taakopdracht.applicatie.naam}: taakopdracht_id: {taakopdracht.id}"

        eerste_taakgebeurtenis = (
            taakopdracht.taakgebeurtenissen_voor_taakopdracht.order_by(
                "aangemaakt_op"
            ).first()
        )
        if eerste_taakgebeurtenis != taakgebeurtenis:
            raise MeldingManager.TaakgebeurtenisOntbreekt(
                f"De eerste taakgebeurtenis moet de huidige zijn. taakopdracht_id: {taakopdracht.id}"
            )

        taakapplicatie_data = {
            "taaktype": taakopdracht.taaktype,
            "titel": taakopdracht.titel,
            "bericht": taakopdracht.bericht,
            "taakopdracht": taakopdracht.get_absolute_url(),
            "melding": taakopdracht.melding.get_absolute_url(),
            "gebruiker": taakgebeurtenis.gebruiker,
            "additionele_informatie": taakopdracht.additionele_informatie,
        }
        taak_aanmaken_response = taakopdracht.applicatie.taak_aanmaken(
            taakapplicatie_data
        )

        if taak_aanmaken_response.status_code != 201:
            response_text = ""
            try:
                response_text = f", antwoord: {taak_aanmaken_response.json()}"
            except Exception:
                ...
            raise Exception(
                f"De taak kon niet worden aangemaakt in {taakopdracht.applicatie.naam}, fout code: {taak_aanmaken_response.status_code}{response_text}"
            )

        taakopdracht.taak_url = (
            taak_aanmaken_response.json().get("_links", {}).get("self")
        )
        taakopdracht.save()
        additionele_informatie = {}
        additionele_informatie.update(taakgebeurtenis.additionele_informatie)
        additionele_informatie.update({"taak_url": taakopdracht.taak_url})
        taakgebeurtenis.additionele_informatie = additionele_informatie
        taakgebeurtenis.save()

        Applicatie.melding_veranderd_notificatie(
            taakopdracht.melding.get_absolute_url(), "taakopdracht_aangemaakt"
        )

    return f"De taak is aangemaakt in {taakopdracht.applicatie.naam}, o.b.v. taakopdracht met id: {taakopdracht.id}"


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_taak_status_aanpassen(self, taakgebeurtenis_id):
    from apps.applicaties.models import Applicatie
    from apps.meldingen.managers import MeldingManager
    from apps.taken.models import Taakgebeurtenis

    with transaction.atomic():
        try:
            taakgebeurtenis = (
                Taakgebeurtenis.objects.using(settings.DEFAULT_DATABASE_KEY)
                .select_for_update(nowait=True)
                .get(id=taakgebeurtenis_id)
            )
        except OperationalError:
            raise MeldingManager.TaakgebeurtenisInGebruik(
                "De taakgebeurtenis is op dit moment in gebruik, probeer het later nog eens."
            )

        taakopdracht = taakgebeurtenis.taakopdracht

        if not taakopdracht.taak_url:
            raise MeldingManager.TaakopdrachtUrlOntbreekt(
                f"Taak is nog niet aangemaakt bij {taakopdracht.applicatie.naam}: taakopdracht_id: {taakopdracht.id}"
            )

        if taakgebeurtenis.additionele_informatie.get("taak_url"):
            logger.error(
                f"Deze status is al aangepast in {taakopdracht.applicatie.naam}: taakopdracht_id: {taakopdracht.id}"
            )

        taakopdracht.taakgebeurtenissen_voor_taakopdracht.all().order_by(
            "aangemaakt_op"
        )

        eerstvolgende_taakgebeurtenissen = (
            taakopdracht.taakgebeurtenissen_voor_taakopdracht.order_by(
                "-aangemaakt_op"
            ).filter(
                additionele_informatie__taak_url__isnull=True,
                aangemaakt_op__gte=taakgebeurtenis.aangemaakt_op,
            )
        )
        eerstvolgende_taakgebeurtenis = eerstvolgende_taakgebeurtenissen.first()

        if eerstvolgende_taakgebeurtenis != taakgebeurtenis:
            raise MeldingManager.TaakgebeurtenisFout(
                f"Deze status aanpassing moeten wachten tot andere statussen doorgegeven zijn: taakopdracht id: {taakopdracht.id}"
            )

        taak_status_aanpassen_data = {
            "taakstatus": {"naam": taakgebeurtenis.taakstatus.naam},
            "bijlagen": [
                bijlage.get_absolute_url() for bijlage in taakgebeurtenis.bijlagen.all()
            ],
            "resolutie": taakopdracht.resolutie,
            "omschrijving_intern": taakgebeurtenis.omschrijving_intern,
            "gebruiker": taakgebeurtenis.gebruiker,
            "uitvoerder": taakgebeurtenis.additionele_informatie.get("uitvoerder"),
        }
        taak_status_aanpassen_response = taakopdracht.applicatie.taak_status_aanpassen(
            f"{taakopdracht.taak_url}status-aanpassen/",
            data=taak_status_aanpassen_data,
        )

        if taak_status_aanpassen_response.status_code not in [200, 404]:
            raise MeldingManager.TaakStatusAanpassenFout(
                f"De taakstatus kon niet worden aangepast: {taakopdracht.taak_url}status-aanpassen/"
            )

        additionele_informatie = {}
        additionele_informatie.update(taakgebeurtenis.additionele_informatie)
        additionele_informatie.update({"taak_url": taakopdracht.taak_url})
        taakgebeurtenis.additionele_informatie = additionele_informatie
        taakgebeurtenis.save()

        Applicatie.melding_veranderd_notificatie(
            taakopdracht.melding.get_absolute_url(), "taakopdracht_status_aangepast"
        )

    return f"De taak status is aangepast in {taakopdracht.applicatie.naam}, o.b.v. taakopdracht met id: {taakopdracht.id}"
