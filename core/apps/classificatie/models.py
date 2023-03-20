from django.contrib.gis.db import models
from django_extensions.db.fields import AutoSlugField


class Onderwerp(models.Model):
    naam = models.CharField(max_length=100)
    slug = AutoSlugField(
        populate_from=("naam",), blank=False, overwrite=False, editable=False
    )

    class Meta:
        verbose_name = "Onderwerp"
        verbose_name_plural = "Onderwerpen"
