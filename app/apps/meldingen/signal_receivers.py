from apps.meldingen.managers import (
    aangemaakt,
    gebeurtenis_toegevoegd,
    status_aangepast,
    taakopdracht_aanmaken,
)
from apps.meldingen.tasks import task_aanmaken_afbeelding_versies
from django.dispatch import receiver


@receiver(aangemaakt, dispatch_uid="melding_aangemaakt")
def aangemaakt_handler(sender, melding, *args, **kwargs):
    for bijlage in melding.bijlagen.all():
        task_aanmaken_afbeelding_versies.delay(bijlage.pk)


@receiver(status_aangepast, dispatch_uid="melding_status_aangepast")
def status_aangepast_handler(sender, melding, status, vorige_status, *args, **kwargs):
    ...


@receiver(gebeurtenis_toegevoegd, dispatch_uid="melding_gebeurtenis_toegevoegd")
def gebeurtenis_toegevoegd_handler(sender, melding, *args, **kwargs):
    ...


@receiver(taakopdracht_aanmaken, dispatch_uid="melding_taakopdracht_aanmaken")
def taakopdracht_aanmaken_handler(sender, taakopdracht, melding, *args, **kwargs):
    ...
