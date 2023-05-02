from django.contrib.gis.db import models


class AdresQuerySet(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(locatie_type="adres")

    def create(self, **kwargs):
        kwargs.update({"locatie_type": "adres"})
        return super().create(**kwargs)


class LichtmastQuerySet(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(locatie_type="lichtmast")

    def create(self, **kwargs):
        kwargs.update({"locatie_type": "lichtmast"})
        return super().create(**kwargs)


class GrafQuerySet(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(locatie_type="graf")

    def create(self, **kwargs):
        kwargs.update({"locatie_type": "graf"})
        return super().create(**kwargs)
