from celery import Task, shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError, transaction

logger = get_task_logger(__name__)

DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6
RETRY_BACKOFF_MAX = 60 * 30
RETRY_BACKOFF = 120


class BaseTaskWithRetry(Task):
    autoretry_for = (Exception,)
    max_retries = MAX_RETRIES
    default_retry_delay = DEFAULT_RETRY_DELAY
    retry_backoff_max = RETRY_BACKOFF_MAX
    retry_backoff = RETRY_BACKOFF
    retry_jitter = True


def get_taak_data(taakopdracht):
    if taakopdracht.applicatie:
        taak_response = taakopdracht.applicatie._do_request(
            taakopdracht.taak_url if taakopdracht.taak_url else "/ditgaatmis"
        )
        if taak_response.status_code == 200:
            return taak_response.json()
        if taak_response.status_code == 404:
            logger.warning(
                f"Fix taakopdracht issues, Fixer taak not found for taakopdracht id: {taakopdracht.id}, taak_url: {taakopdracht.taak_url}, status code: {taak_response.status_code}"
            )
            return "404 Fixer taak not found"
        logger.error(
            f"Fix taakopdracht issues, Fixer taak ophalen error. Status code: {taak_response.status_code}, taakopdracht id: {taakopdracht.id}, taak_url: {taakopdracht.taak_url}, response_text={taak_response.text}"
        )
        taak_response.raise_for_status()


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_fix_taakopdracht_issues(self, taakopdracht_id):
    from apps.taken.models import Taakopdracht

    taakopdracht = Taakopdracht.objects.get(id=taakopdracht_id)
    taakgebeurtenis = (
        taakopdracht.taakgebeurtenissen_voor_taakopdracht.filter(
            taakstatus=taakopdracht.status
        )
        .order_by("-aangemaakt_op")
        .first()
    )
    # Issue: Fix missing afgesloten_op voor geannuleerde taken
    if not taakopdracht.afgesloten_op and taakopdracht.resolutie == "geannuleerd":
        taakopdracht.afgesloten_op = taakgebeurtenis.aangemaakt_op
        taakopdracht.save()
        logger.warning(
            f"Taakopdracht: {taakopdracht_id} now has a afgesloten_op: {taakopdracht.afgesloten_op} ."
        )
    # Issue: Fix missing afhandeltijd voor voltooide taken
    if (
        not taakopdracht.afhandeltijd
        and taakopdracht.afgesloten_op
        and taakopdracht.aangemaakt_op
        and taakopdracht.resolutie == "geannuleerd"
    ):
        taakopdracht.afhandeltijd = (
            taakopdracht.afgesloten_op - taakopdracht.aangemaakt_op
        )
        taakopdracht.save()
        logger.warning(
            f"Taakopdracht: {taakopdracht_id} now has a afhandeltijd: {taakopdracht.afhandeltijd} ."
        )
    # Issue: FixeR taak for taakopdracht was never created
    taak_data = get_taak_data(taakopdracht)
    if (
        taak_data
        and taak_data == "404 Fixer taak not found"
        and taakopdracht.applicatie
    ):
        logger.warning(
            f"Creating new taak for taakopdracht met id: {taakopdracht_id}, taakgebeurtenis met id: {taakgebeurtenis.id}"
        )
        task_taak_aanmaken.delay(
            taakgebeurtenis_id=taakgebeurtenis.id, check_taak_url=False
        )
    # Issue: Taakopdracht has voltooid in mor-core but not in fixer
    elif (
        taak_data
        and not isinstance(taak_data, str)
        and taakopdracht.status.naam == "voltooid"
        and taakopdracht.status.naam != taak_data.get("taakstatus").get("naam")
        and taakopdracht.applicatie
    ):
        logger.warning(
            f"Updating taak status for taakopdracht met id: {taakopdracht_id}, taakgebeurtenis met id: {taakgebeurtenis.id} en FixeR taak met id: {taak_data.get('id')}"
        )
        task_taak_status_aanpassen.delay(
            taakgebeurtenis_id=taakgebeurtenis.id, voorkom_dubbele_sync=False
        )


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_taak_aanmaken(self, taakgebeurtenis_id, check_taak_url=True):
    from apps.meldingen.managers import MeldingManager
    from apps.taken.models import Taakgebeurtenis, Taakopdracht

    with transaction.atomic():
        try:
            taakgebeurtenis = (
                Taakgebeurtenis.objects.using(settings.DEFAULT_DATABASE_KEY)
                .select_for_update(nowait=True)
                .get(id=taakgebeurtenis_id)
            )
        except ObjectDoesNotExist:
            raise MeldingManager.TaakgebeurtenisNietGevonden(
                f"Taakgebeurtenis met id {taakgebeurtenis_id} bestaat niet."
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
        except ObjectDoesNotExist:
            raise MeldingManager.TaakopdrachtNietGevonden(
                f"Taakopdracht met id {taakgebeurtenis.taakopdracht.id} bestaat niet."
            )
        except OperationalError:
            raise MeldingManager.TaakopdrachtInGebruik(
                "De taakopdracht is op dit moment in gebruik, probeer het later nog eens."
            )

        if taakopdracht.taak_url and check_taak_url:
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
            logger.error(
                f"De taak kon niet worden aangemaakt in {taakopdracht.applicatie.naam} o.b.v. taakopdracht met id {taakopdracht.id}, fout code: {taak_aanmaken_response.status_code}{response_text}"
            )
            raise Exception(
                f"De taak kon niet worden aangemaakt in {taakopdracht.applicatie.naam} o.b.v. taakopdracht met id {taakopdracht.id}, fout code: {taak_aanmaken_response.status_code}{response_text}"
            )

        taak_aanmaken_data = taak_aanmaken_response.json()
        taakopdracht.taak_url = taak_aanmaken_data.get("_links", {}).get("self")
        taakopdracht.save()
        additionele_informatie = {}
        additionele_informatie.update(taakgebeurtenis.additionele_informatie)
        additionele_informatie.update({"taak_url": taakopdracht.taak_url})
        taakgebeurtenis.additionele_informatie = additionele_informatie
        taakgebeurtenis.save()

        # Applicatie.melding_veranderd_notificatie(
        #     taakopdracht.melding.get_absolute_url(), "taakopdracht_aangemaakt"
        # )
    logger.warning(
        f"De taak is aangemaakt in {taakopdracht.applicatie.naam}, o.b.v. taakopdracht met id: {taakopdracht.id} en FixeR taak met id: {taak_aanmaken_data.get('id')}."
    )
    return f"De taak is aangemaakt in {taakopdracht.applicatie.naam}, o.b.v. taakopdracht met id: {taakopdracht.id} en FixeR taak met id: {taak_aanmaken_data.get('id')}."


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_taak_status_aanpassen(self, taakgebeurtenis_id, voorkom_dubbele_sync=True):
    from apps.meldingen.managers import MeldingManager
    from apps.taken.models import Taakgebeurtenis

    with transaction.atomic():
        try:
            taakgebeurtenis = (
                Taakgebeurtenis.objects.using(settings.DEFAULT_DATABASE_KEY)
                .select_for_update(nowait=True)
                .get(id=taakgebeurtenis_id)
            )
        except ObjectDoesNotExist:
            raise MeldingManager.TaakgebeurtenisNietGevonden(
                f"Taakgebeurtenis met id {taakgebeurtenis_id} bestaat niet."
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
            error = f"Deze status is al aangepast in {taakopdracht.applicatie.naam}: taakopdracht_id: {taakopdracht.id}"
            logger.error(error)
            if voorkom_dubbele_sync:
                return error

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
            logger.error(
                f"De taakstatus kon niet worden aangepast: {taakopdracht.taak_url}status-aanpassen/ o.b.v. taakopdracht met id: {taakopdracht.id}"
            )
            raise MeldingManager.TaakStatusAanpassenFout(
                f"De taakstatus kon niet worden aangepast: {taakopdracht.taak_url}status-aanpassen/ o.b.v. taakopdracht met id: {taakopdracht.id}"
            )

        taak_status_aanpassen_data = taak_status_aanpassen_response.json()
        additionele_informatie = {}
        additionele_informatie.update(taakgebeurtenis.additionele_informatie)
        additionele_informatie.update({"taak_url": taakopdracht.taak_url})
        taakgebeurtenis.additionele_informatie = additionele_informatie
        taakgebeurtenis.save()

    resultaat = f"De taak status is aangepast in {taakopdracht.applicatie.naam}, o.b.v. taakopdracht met id: {taakopdracht.id} en FixeR taak met id: {taak_status_aanpassen_data.get('id')}."
    logger.warning(resultaat)
    return resultaat
