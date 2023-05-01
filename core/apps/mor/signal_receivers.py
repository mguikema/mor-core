import copy

from apps.mor.managers import aangemaakt, status_aangepast
from apps.mor.models import Bijlage, Melding, Signaal
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=Signaal, dispatch_uid="add_melding_to_signaal")
def add_melding_to_signaal(sender, instance, **kwargs):
    if kwargs.get("raw"):
        return
    if not instance.melding:
        instance.melding = Melding.acties.aanmaken(instance)


@receiver(post_save, sender=Bijlage, dispatch_uid="add_bijlage_to_melding")
def add_relation_to_melding(sender, instance, created, **kwargs):
    if kwargs.get("raw"):
        return
    sct = ContentType.objects.get_for_model(Signaal)
    mct = ContentType.objects.get_for_model(Melding)
    valid_relation = sender.__name__ in ("Bijlage",)
    if created and valid_relation and instance.content_type == sct:
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


@receiver(status_aangepast, dispatch_uid="melding_status_aangepast")
def status_aangepast_handler(sender, melding, status, vorige_status, *args, **kwargs):
    ...


@receiver(aangemaakt, dispatch_uid="melding_aangemaakt")
def aangemaakt_handler(sender, melding, *args, **kwargs):
    ...
