from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from utils.models import BasisModel


class Notificatie(BasisModel):
    class ActieType(models.TextChoices):
        AANGEMAAKT = "aangemaakt", "Aangemaakt"
        GEWIJZIGD = "gewijzigd", "Gewijzigd"
        VERWIJDERD = "verwijderd", "Verwijderd"

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    actie = models.CharField(
        max_length=100,
        choices=ActieType.choices,
    )
    additionele_informatie = models.JSONField(default=dict)

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Notificatie"
        verbose_name_plural = "Notificaties"
