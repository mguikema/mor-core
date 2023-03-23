import copy

from apps.locatie.models import Adres, Geometrie, Graf, Lichtmast
from apps.mor.models import Bijlage, Melding, Signaal
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=Signaal, dispatch_uid="add_melding_to_signaal")
def add_melding_to_signaal(sender, instance, **kwargs):
    if kwargs.get("raw"):
        return
    if not instance.melding:
        melding = None  # Signaal.objects.filter_to_get_melding(instance)
        if not melding:
            melding = Melding.objects.create_from_signaal(instance)
        instance.melding = melding


@receiver(
    post_save, sender=Lichtmast, dispatch_uid="add_locations_to_melding_lichtmast"
)
@receiver(
    post_save, sender=Geometrie, dispatch_uid="add_locations_to_melding_geometrie"
)
@receiver(post_save, sender=Adres, dispatch_uid="add_locations_to_melding_adres")
@receiver(post_save, sender=Graf, dispatch_uid="add_locations_to_melding_graf")
@receiver(post_save, sender=Bijlage, dispatch_uid="add_locations_to_melding_bijlage")
def add_locations_to_melding(sender, instance, created, **kwargs):
    if kwargs.get("raw"):
        return
    sct = ContentType.objects.get_for_model(Signaal)
    mct = ContentType.objects.get_for_model(Melding)
    valid_relation = sender.__name__ in (
        "Graf",
        "Lichtmast",
        "Adres",
        "Geometrie",
        "Bijlage",
    )
    if (
        created
        and valid_relation
        and instance.content_type == sct
        and not hasattr(instance.content_type, "melding")
    ):
        data = copy.deepcopy(instance.__dict__)
        data = {
            k: v
            for k, v in data.items()
            if k
            not in (
                "_state",
                "id",
                "uuid",
                "aangemaakt_op",
                "aangepast_op",
                "content_type_id",
            )
        }
        data.update(
            {
                "content_type": mct,
                "object_id": instance.content_object.melding.id,
            }
        )
        sender.objects.create(**data)
