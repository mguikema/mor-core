from apps.locatie.models import Locatie
from celery import Task, shared_task
from celery.utils.log import get_task_logger
from django.db import transaction

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


@shared_task(bind=True, base=BaseTaskWithRetry)
def update_locatie_zoek_field_task(self, batch_size=1000):
    total_count = Locatie.objects.count()
    for start in range(0, total_count, batch_size):
        end = start + batch_size
        update_batch.delay(start, end)
    return f"Queued update for {total_count} locations in batches of {batch_size}"


@shared_task(bind=True, base=BaseTaskWithRetry)
def update_batch(self, start, end):
    with transaction.atomic():
        for locatie in Locatie.objects.all()[start:end]:
            if not locatie.locatie_zoek_field:
                locatie.update_locatie_zoek_field()
                locatie.save()
        return f"Updated locations from {start} to {end}"
