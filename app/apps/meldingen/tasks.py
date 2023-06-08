import celery
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

DEFAULT_RETRY_DELAY = 2
MAX_RETRIES = 6

LOCK_EXPIRE = 5


class BaseTaskWithRetry(celery.Task):
    autoretry_for = (Exception,)
    max_retries = MAX_RETRIES
    default_retry_delay = DEFAULT_RETRY_DELAY


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_aanmaken_afbeelding_versies(self, bijlage_id):
    from apps.meldingen.models import Bijlage

    bijlage_instance = Bijlage.objects.get(id=bijlage_id)
    bijlage_instance.aanmaken_afbeelding_versies()
    bijlage_instance.save()

    return f"Bijlage id: {bijlage_instance.id}"


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_notificatie_voor_signaal_melding_afgesloten(self, signaal_id):
    from apps.meldingen.models import Signaal

    signaal_instantie = Signaal.objects.get(pk=signaal_id)
    signaal_instantie.notificatie_melding_afgesloten()

    return f"Signaal id: {signaal_instantie.pk}"
