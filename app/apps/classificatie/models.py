from django.contrib.gis.db import models
from django_extensions.db.fields import AutoSlugField


class OnderwerpBasis(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(
        populate_from=("name",), blank=False, overwrite=False, editable=False
    )

    def __str__(self) -> str:
        return f"{self.pk} - {self.name}"

    class Meta:
        abstract = True


class OnderwerpGroep(OnderwerpBasis):
    class Meta:
        unique_together = ("slug",)
        verbose_name = "Onderwerp groep"
        verbose_name_plural = "Onderwerp groepen"


class Onderwerp(OnderwerpBasis):
    onderwerp_groep = models.ForeignKey(
        to="classificatie.OnderwerpGroep",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = (
            "slug",
            "onderwerp_groep",
        )
        verbose_name = "Onderwerp"
        verbose_name_plural = "Onderwerpen"
