import logging

from apps.bijlagen.models import Bijlage
from apps.meldingen.managers import MeldingManager
from apps.meldingen.querysets import MeldingQuerySet
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from utils.models import BasisModel

logger = logging.getLogger(__name__)


class Meldinggebeurtenis(BasisModel):
    """
    MeldingGebeurtenissen bouwen de history op van van de melding
    """

    class GebeurtenisType(models.TextChoices):
        STANDAARD = "standaard", "Standaard"
        STATUS_WIJZIGING = "status_wijziging", "Status wijziging"
        MELDING_AANGEMAAKT = "melding_aangemaakt", "Melding aangemaakt"
        TAAKOPDRACHT_AANGEMAAKT = "taakopdracht_aangemaakt", "Taakopdracht aangemaakt"
        TAAKOPDRACHT_STATUS_WIJZIGING = (
            "taakopdracht_status_wijziging",
            "Taakopdracht status wijziging",
        )

    gebeurtenis_type = models.CharField(
        max_length=40,
        choices=GebeurtenisType.choices,
        default=GebeurtenisType.STANDAARD,
    )

    bijlagen = GenericRelation(Bijlage)
    status = models.OneToOneField(
        to="status.Status",
        related_name="meldinggebeurtenis_voor_status",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    omschrijving_intern = models.CharField(max_length=5000, null=True, blank=True)
    omschrijving_extern = models.CharField(max_length=2000, null=True, blank=True)
    gebruiker = models.CharField(max_length=200, null=True, blank=True)
    melding = models.ForeignKey(
        to="meldingen.Melding",
        related_name="meldinggebeurtenissen_voor_melding",
        on_delete=models.CASCADE,
    )
    taakopdracht = models.ForeignKey(
        to="taken.Taakopdracht",
        related_name="meldinggebeurtenissen_voor_taakopdracht",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    taakgebeurtenis = models.ForeignKey(
        to="taken.Taakgebeurtenis",
        related_name="meldinggebeurtenissen_voor_taakgebeurtenis",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Melding gebeurtenis"
        verbose_name_plural = "Melding gebeurtenissen"


class Melding(BasisModel):
    """
    Een melding is de ontdubbelde versie van signalen
    """

    """
    Als er geen taak_applicaties zijn linked aan deze melding, kan b.v. MidOffice deze handmatig toewijzen
    """

    class ResolutieOpties(models.TextChoices):
        OPGELOST = "opgelost", "Opgelost"
        NIET_OPGELOST = "niet_opgelost", "Niet opgelost"

    origineel_aangemaakt = models.DateTimeField()
    omschrijving_kort = models.CharField(max_length=500)
    omschrijving = models.CharField(max_length=5000, null=True, blank=True)
    afgesloten_op = models.DateTimeField(null=True, blank=True)
    meta = models.JSONField(default=dict)
    meta_uitgebreid = models.JSONField(default=dict)
    status = models.OneToOneField(
        to="status.Status",
        related_name="melding_voor_status",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    resolutie = models.CharField(
        max_length=50,
        choices=ResolutieOpties.choices,
        default=ResolutieOpties.NIET_OPGELOST,
    )
    bijlagen = GenericRelation(Bijlage)
    onderwerpen = models.ManyToManyField(
        to="aliassen.OnderwerpAlias",
        related_name="meldingen_voor_onderwerpen",
        blank=True,
    )

    objects = MeldingQuerySet.as_manager()
    acties = MeldingManager()

    @property
    def get_graven(self):
        return self.locaties_voor_melding

    @property
    def get_lichtmasten(self):
        return self.locaties_voor_melding

    @property
    def get_adressen(self):
        return self.locaties_voor_melding

    def actieve_taakopdrachten(self):
        return self.taakopdrachten_voor_melding.exclude(status__naam="voltooid")

    class Meta:
        verbose_name = "Melding"
        verbose_name_plural = "Meldingen"
