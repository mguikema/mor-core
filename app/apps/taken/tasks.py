import celery
from apps.taken.models import Taakopdracht
from apps.taken.serializers import TaakopdrachtSerializer
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from rest_framework.reverse import reverse

logger = get_task_logger(__name__)

DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6

LOCK_EXPIRE = 5


class BaseTaskWithRetry(celery.Task):
    autoretry_for = (Exception,)
    max_retries = MAX_RETRIES
    default_retry_delay = DEFAULT_RETRY_DELAY


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
def fix_taakopdracht_issues(self, taakopdracht_id):
    taakopdracht = Taakopdracht.objects.get(id=taakopdracht_id)
    taakgebeurtenis = (
        taakopdracht.taakgebeurtenissen_voor_taakopdracht.filter(
            taakstatus=taakopdracht.status
        )
        .order_by("-aangemaakt_op")
        .first()
    )
    # Fix missing afgesloten_op voor geannulleerde taken
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
    # Issue: taakopdracht has voltooid in mor-core but not in fixer
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
