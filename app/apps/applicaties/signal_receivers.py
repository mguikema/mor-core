from apps.applicaties.models import Applicatie
from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(
    pre_save, sender=Applicatie, dispatch_uid="haal_taaktypes_voor_taakapplicatie"
)
def haal_taaktypes_voor_taakapplicatie(sender, instance, **kwargs):
    if kwargs.get("raw"):
        return
    instance.haal_taaktypes()