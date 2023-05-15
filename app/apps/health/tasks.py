import time

from apps.meldingen.models import Melding
from config.celery import app as celery_app


@celery_app.task
def do_some_queries():
    time.sleep(10)
    return Melding.objects.count()


@celery_app.task
def query_every_five_mins():
    return Melding.objects.count()
