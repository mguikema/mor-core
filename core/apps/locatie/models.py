from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from utils.models import BasisModel


class LocatieBasis(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    bron = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        abstract = True


class GeometrieBasis(models.Model):
    """
    Basis klasse voor geografische informatie.
    """

    geometrie = models.GeometryField()

    class Meta:
        abstract = True


class AdresBasis(models.Model):
    """
    Basis klasse voor adres informatie.
    """

    plaatsnaam = models.CharField(max_length=255)
    straatnaam = models.CharField(max_length=255, null=True, blank=True)
    huisnummer = models.IntegerField(null=True, blank=True)
    huisletter = models.CharField(max_length=1, null=True, blank=True)
    toevoeging = models.CharField(max_length=4, null=True, blank=True)
    postcode = models.CharField(max_length=7, null=True, blank=True)

    class Meta:
        abstract = True


class LichtmastBasis(models.Model):
    """
    Basis klasse voor lichtmast informatie.
    """

    lichtmast = models.CharField(max_length=255)

    class Meta:
        abstract = True


# Concrete modellen


class Geometrie(BasisModel, GeometrieBasis, LocatieBasis):
    """
    Klasse voor het opslaan van geografische informatie.
    """


class Adres(BasisModel, AdresBasis, LocatieBasis):
    """
    Klasse voor het opslaan van adres informatie.
    """

    geometrieen = GenericRelation(Geometrie)


class Graf(BasisModel, LocatieBasis):
    """
    Klasse voor het opslaan van graf locatie informatie.
    """

    plaatsnaam = models.CharField(max_length=255)
    begraafplaats = models.CharField(max_length=50)
    grafnummer = models.CharField(max_length=10)
    vak = models.CharField(max_length=10, null=True, blank=True)
    geometrieen = GenericRelation(Geometrie)


class Lichtmast(BasisModel, LichtmastBasis, LocatieBasis):
    """
    Klasse voor het opslaan van geografische met lichtmast informatie.
    """

    geometrieen = GenericRelation(Geometrie)
