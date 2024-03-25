from apps.applicaties.models import Applicatie
from apps.bijlagen.tasks import task_aanmaken_afbeelding_versies
from apps.meldingen.managers import (
    afgesloten,
    gebeurtenis_toegevoegd,
    signaal_aangemaakt,
    status_aangepast,
    taakopdracht_aangemaakt,
    taakopdracht_status_aangepast,
    urgentie_aangepast,
)
from apps.meldingen.tasks import task_notificatie_voor_signaal_melding_afgesloten
from apps.status.models import Status
from django.dispatch import receiver


@receiver(signaal_aangemaakt, dispatch_uid="melding_signaal_aangemaakt")
def signaal_aangemaakt_handler(sender, melding, signaal, *args, **kwargs):
    Applicatie.melding_veranderd_notificatie(
        melding.get_absolute_url(), "signaal_aangemaakt"
    )
    for bijlage in signaal.bijlagen.all():
        task_aanmaken_afbeelding_versies.delay(bijlage.pk)


@receiver(status_aangepast, dispatch_uid="melding_status_aangepast")
def status_aangepast_handler(sender, melding, status, vorige_status, *args, **kwargs):
    Applicatie.melding_veranderd_notificatie(
        melding.get_absolute_url(), "status_aangepast"
    )
    if melding.afgesloten_op and melding.status.naam == Status.NaamOpties.AFGEHANDELD:
        afgesloten.send_robust(
            sender=sender,
            melding=melding,
        )


@receiver(urgentie_aangepast, dispatch_uid="melding_urgentie_aangepast")
def urgentie_aangepast_handler(sender, melding, vorige_urgentie, *args, **kwargs):
    Applicatie.melding_veranderd_notificatie(
        melding.get_absolute_url(), "urgentie_aangepast"
    )


@receiver(afgesloten, dispatch_uid="melding_afgesloten")
def afgesloten_handler(sender, melding, *args, **kwargs):
    Applicatie.melding_veranderd_notificatie(melding.get_absolute_url(), "afgesloten")
    for signaal in melding.signalen_voor_melding.all():
        task_notificatie_voor_signaal_melding_afgesloten.delay(signaal.pk)


@receiver(gebeurtenis_toegevoegd, dispatch_uid="melding_gebeurtenis_toegevoegd")
def gebeurtenis_toegevoegd_handler(
    sender, meldinggebeurtenis, melding, *args, **kwargs
):
    Applicatie.melding_veranderd_notificatie(
        melding.get_absolute_url(), "gebeurtenis_toegevoegd"
    )
    for bijlage in meldinggebeurtenis.bijlagen.all():
        task_aanmaken_afbeelding_versies.delay(bijlage.pk)


@receiver(taakopdracht_aangemaakt, dispatch_uid="taakopdracht_aangemaakt")
def taakopdracht_aangemaakt_handler(sender, taakopdracht, melding, *args, **kwargs):
    Applicatie.melding_veranderd_notificatie(
        melding.get_absolute_url(), "taakopdracht_aangemaakt"
    )


@receiver(taakopdracht_status_aangepast, dispatch_uid="taakopdracht_status_aangepast")
def taakopdracht_status_aangepast_handler(
    sender, melding, taakopdracht, taakgebeurtenis, *args, **kwargs
):
    Applicatie.melding_veranderd_notificatie(
        melding.get_absolute_url(), "taakopdracht_status_aangepast"
    )
    for bijlage in taakgebeurtenis.bijlagen.all():
        task_aanmaken_afbeelding_versies.delay(bijlage.pk)
