from apps.mor.models import Melding, Signaal
from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=Signaal, dispatch_uid="add_melding_to_signaal")
def add_melding_to_signaal(sender, instance, **kwargs):
    if kwargs.get("raw"):
        return
    if not instance.melding:
        melding = None  # Signaal.objects.filter_to_get_melding(instance)
        if not melding:
            melding = Melding.objects.create()
        instance.melding = melding
