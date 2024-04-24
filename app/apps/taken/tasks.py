import celery
from apps.taken.models import Taakopdracht
from apps.taken.serializers import TaakopdrachtSerializer
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db import OperationalError
from rest_framework.reverse import reverse

logger = get_task_logger(__name__)

DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6
LOCK_EXPIRE = 5
RETRY_BACKOFF_MAX = 60 * 30
RETRY_BACKOFF = 120


class BaseTaskWithRetry(celery.Task):
    autoretry_for = (Exception,)
    max_retries = MAX_RETRIES
    default_retry_delay = DEFAULT_RETRY_DELAY
    retry_backoff_max = RETRY_BACKOFF_MAX
    retry_backoff = RETRY_BACKOFF
    retry_jitter = True


def get_taak_data(taakopdracht):
    if taakopdracht.applicatie:
        taak_response = taakopdracht.applicatie._do_request(taakopdracht.taak_url)
        if taak_response.status_code == 200:
            return taak_response.json()
        if taak_response.status_code == 404:
            logger.warning(
                f"Fix taakopdracht issues, Fixer taak not found for taakopdracht id: {taakopdracht.id}, taak_url: {taakopdracht.taak_url}, status code: {taak_response.status_code}, response_text={taak_response.text}"
            )
            return "404 Fixer taak not found"
        logger.error(
            f"Fix taakopdracht issues, Fixer taak ophalen error. Status code: {taak_response.status_code}, taakopdracht id: {taakopdracht.id}, taak_url: {taakopdracht.taak_url}, response_text={taak_response.text}"
        )
        taak_response.raise_for_status()


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_fix_taakopdracht_issues(self, taakopdracht_id):
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
    # Issue: FixeR taak for taakopdracht was never created
    taak_data = get_taak_data(taakopdracht)
    if (
        taak_data
        and taak_data == "404 Fixer taak not found"
        and taakopdracht.applicatie
    ):
        serializer = TaakopdrachtSerializer(instance=taakopdracht)
        basis_url = settings.APPLICATIE_BASIS_URL
        taakapplicatie_data = {
            "_links": {
                "self": basis_url + serializer.data["_links"]["self"],
                "applicatie": basis_url + serializer.data["_links"]["applicatie"],
                "melding": basis_url + serializer.data["_links"]["melding"],
            },
            "taaktype": serializer.data["taaktype"],
            "titel": serializer.data["titel"],
            "bericht": serializer.data["bericht"],
            "additionele_informatie": serializer.data["additionele_informatie"],
            "status": serializer.data["status"],
            "resolutie": serializer.data["resolutie"],
            "gebruiker": taakgebeurtenis.gebruiker,
            "taakopdracht": basis_url
            + reverse(
                "v1:taakopdracht-detail",
                kwargs={"uuid": taakopdracht.uuid},
            ),
        }
        taakapplicatie_data["melding"] = taakapplicatie_data.get("_links", {}).get(
            "melding"
        )

        taak_aanmaken_response = taakopdracht.applicatie.taak_aanmaken(
            taakapplicatie_data
        )

        if taak_aanmaken_response.status_code == 201:
            taak_aanmaken_data = taak_aanmaken_response.json()
            taakopdracht.taak_url = taak_aanmaken_data.get("_links", {}).get("self")
            taakopdracht.save()
            logger.warning(
                f"Taak in FixeR aangemaakt successfully for Mor-Core taakopdracht.id: {taakopdracht_id} and FixeR taak.id: {taak_aanmaken_data.get('id')}."
            )
            return {
                "taakopdracht.id": taakopdracht_id,
                "taak.id": taak_aanmaken_data.get("id"),
            }
        else:
            logger.error(
                f"Fix taakopdracht issues, taak_aanmaken_response: status_code={taak_aanmaken_response.status_code}, taakopdracht.id={taakopdracht_id}, taak.id={taak_data.get('id')}, aanmaak_data={taakapplicatie_data}, error text: {taak_aanmaken_response.text}"
            )
            return {
                "taakopdracht.id": taakopdracht_id,
                "taak_aanmaken_response.status_code": taak_aanmaken_response.status_code,
                "taak_aanmaken_response.text": taak_aanmaken_response.text,
            }
    # Issue: Taakopdracht has voltooid in mor-core but not in fixer
    elif (
        taak_data
        and not isinstance(taak_data, str)
        and taakopdracht.status.naam == "voltooid"
        and taakopdracht.status.naam != taak_data.get("taakstatus").get("naam")
        and taakopdracht.applicatie
    ):
        taak_status_aanpassen_data = {
            "taakstatus": {"naam": taakgebeurtenis.taakstatus.naam},
            "resolutie": taakopdracht.resolutie,
            "omschrijving_intern": taakgebeurtenis.omschrijving_intern,
            "gebruiker": taakgebeurtenis.gebruiker,
            "bijlagen": [],
            # "uitvoerder": uitvoerder,
        }
        taak_status_aanpassen_response = taakopdracht.applicatie.taak_status_aanpassen(
            f"{taakopdracht.taak_url}status-aanpassen/",
            data=taak_status_aanpassen_data,
        )
        if taak_status_aanpassen_response.status_code != 200:
            logger.error(
                f"Fix taakopdracht issues, taak_status_aanpassen_response: status_code={taak_status_aanpassen_response.status_code}, taakopdracht.id={taakopdracht_id}, taak.id={taak_data.get('id')}, update_data={taak_status_aanpassen_data}, error text: {taak_status_aanpassen_response.text}"
            )
            return {
                "taakopdracht.id": taakopdracht_id,
                "taak.id": taak_data.get("id"),
                "taak_status_aanpassen_response.status_code": taak_status_aanpassen_response.status_code,
                "taak_status_aanpassen_response.text": taak_status_aanpassen_response.text,
            }

        else:
            logger.warning(
                f"Taak in FixeR updated successfully for Mor-Core taakopdracht.id: {taakopdracht_id} and FixeR taak.id: {taak_data.get('id')}."
            )
            return {
                "taakopdracht.id": taakopdracht_id,
                "taak.id": taak_data.get("id"),
            }


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_taak_aanmaken(self, taakgebeurtenis_id):
    from apps.applicaties.models import Applicatie
    from apps.meldingen.managers import MeldingManager
    from apps.taken.models import Taakgebeurtenis

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
            Taakgebeurtenis.objects.using(settings.DEFAULT_DATABASE_KEY)
            .select_for_update(nowait=True)
            .get(id=taakgebeurtenis.taakopdracht.id)
        )
    except OperationalError:
        raise MeldingManager.TaakopdrachtInGebruik(
            "De taakopdracht is op dit moment in gebruik, probeer het later nog eens."
        )

    if taakopdracht.taak_url:
        return f"Taak is al aangemaakt bij {taakopdracht.applicatie.naam}: taakopdracht_id: {taakopdracht.id}"

    eerste_taakgebeurtenis = taakopdracht.taakgebeurtenissen_voor_taakopdracht.order_by(
        "aangemaakt_op"
    ).first()
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
    taak_aanmaken_response = taakopdracht.applicatie.taak_aanmaken(taakapplicatie_data)

    if taak_aanmaken_response.status_code != 201:
        response_text = ""
        try:
            response_text = f", antwoord: {taak_aanmaken_response.json()}"
        except Exception:
            ...
        raise Exception(
            f"De taak kon niet worden aangemaakt in {taakopdracht.applicatie.naam}, fout code: {taak_aanmaken_response.status_code}{response_text}"
        )

    taakopdracht.taak_url = taak_aanmaken_response.json().get("_links", {}).get("self")
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

    taakopdracht.taakgebeurtenissen_voor_taakopdracht.all().order_by("aangemaakt_op")

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
