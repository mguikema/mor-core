from apps.meldingen.managers import (
    aangemaakt,
    afgesloten,
    gebeurtenis_toegevoegd,
    status_aangepast,
    taakopdracht_aangemaakt,
    taakopdracht_status_aangepast,
)
from apps.meldingen.tasks import (
    task_aanmaken_afbeelding_versies,
    task_notificatie_voor_signaal_melding_afgesloten,
)
from apps.status.models import Status
from django.dispatch import receiver


@receiver(aangemaakt, dispatch_uid="melding_aangemaakt")
def aangemaakt_handler(sender, melding, *args, **kwargs):
    for bijlage in melding.bijlagen.all():
        task_aanmaken_afbeelding_versies.delay(bijlage.pk)


@receiver(status_aangepast, dispatch_uid="melding_status_aangepast")
def status_aangepast_handler(sender, melding, status, vorige_status, *args, **kwargs):
    if melding.afgesloten_op and melding.status.naam == Status.NaamOpties.AFGEHANDELD:
        afgesloten.send_robust(
            sender=sender,
            melding=melding,
        )


@receiver(afgesloten, dispatch_uid="melding_afgesloten")
def afgesloten_handler(sender, melding, *args, **kwargs):
    for signaal in melding.signalen_voor_melding.all():
        task_notificatie_voor_signaal_melding_afgesloten.delay(signaal.pk)


@receiver(gebeurtenis_toegevoegd, dispatch_uid="melding_gebeurtenis_toegevoegd")
def gebeurtenis_toegevoegd_handler(
    sender, meldinggebeurtenis, melding, *args, **kwargs
):
    for bijlage in meldinggebeurtenis.bijlagen.all():
        task_aanmaken_afbeelding_versies.delay(bijlage.pk)


@receiver(taakopdracht_aangemaakt, dispatch_uid="taakopdracht_aangemaakt")
def taakopdracht_aangemaakt_handler(sender, taakopdracht, melding, *args, **kwargs):
    ...


@receiver(taakopdracht_status_aangepast, dispatch_uid="taakopdracht_status_aangepast")
def taakopdracht_status_aangepast_handler(
    sender, melding, taakopdracht, taakgebeurtenis, *args, **kwargs
):
    for bijlage in taakgebeurtenis.bijlagen.all():
        task_aanmaken_afbeelding_versies.delay(bijlage.pk)
