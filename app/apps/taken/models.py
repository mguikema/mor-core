from apps.bijlagen.models import Bijlage
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from utils.models import BasisModel


class Taakgebeurtenis(BasisModel):
    """
    Taakgebeurtenissen bouwen de history op van een taak
    """

    bijlagen = GenericRelation(Bijlage)
    taakstatus = models.ForeignKey(
        to="taken.Taakstatus",
        related_name="taakgebeurtenissen_voor_taakstatus",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    omschrijving_intern = models.CharField(max_length=5000, null=True, blank=True)
    gebruiker = models.CharField(max_length=200, null=True, blank=True)
    taakopdracht = models.ForeignKey(
        to="taken.Taakopdracht",
        related_name="taakgebeurtenissen_voor_taakopdracht",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taakgebeurtenis"
        verbose_name_plural = "Taakgebeurtenissen"


class Taakstatus(BasisModel):
    class NaamOpties(models.TextChoices):
        NIEUW = "nieuw", "Nieuw"
        BEZIG = "bezig", "Bezig"
        VOLTOOID = "voltooid", "Voltooid"

    naam = models.CharField(
        max_length=50,
        choices=NaamOpties.choices,
        default=NaamOpties.NIEUW,
    )
    taakopdracht = models.ForeignKey(
        to="taken.Taakopdracht",
        related_name="taakstatussen_voor_taakopdracht",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("-aangemaakt_op",)

    def __str__(self) -> str:
        return f"{self.naam}({self.pk})"

    def volgende_statussen(self):
        naam_opties = [no[0] for no in Taakstatus.NaamOpties.choices]
        if self.naam not in naam_opties:
            return naam_opties

        match self.naam:
            case Taakstatus.NaamOpties.NIEUW:
                return [
                    Taakstatus.NaamOpties.BEZIG,
                    Taakstatus.NaamOpties.VOLTOOID,
                ]
            case Taakstatus.NaamOpties.BEZIG:
                return [
                    Taakstatus.NaamOpties.VOLTOOID,
                ]
            case _:
                return []

    class TaakStatusVeranderingNietToegestaan(Exception):
        pass


class Taakopdracht(BasisModel):
    """
    Taakapplicaties kunnen een taakopdracht aanmaken in more-core.
    Op basis van de taakopdracht wordt er een taak aangemaakt in een applicatie.
    In de response zit de taak_url, die weer opgeslagen wordt in deze taakopdracht.
    Zo worden taakopdrachten aan taken gelinked.
    """

    class ResolutieOpties(models.TextChoices):
        OPGELOST = "opgelost", "Opgelost"
        NIET_OPGELOST = "niet_opgelost", "Niet opgelost"
        GEANNULEERD = "geannuleerd", "Geannuleerd"

    afgesloten_op = models.DateTimeField(null=True, blank=True)
    melding = models.ForeignKey(
        to="meldingen.Melding",
        related_name="taakopdrachten_voor_melding",
        on_delete=models.CASCADE,
    )
    applicatie = models.ForeignKey(
        to="applicaties.Applicatie",
        related_name="taakopdrachten_voor_applicatie",
        on_delete=models.CASCADE,
    )
    taaktype = models.CharField(
        max_length=200,
    )
    titel = models.CharField(
        max_length=100,
    )
    bericht = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )
    status = models.ForeignKey(
        to="taken.Taakstatus",
        related_name="taakopdrachten_voor_taakstatus",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    resolutie = models.CharField(
        max_length=50,
        choices=ResolutieOpties.choices,
        blank=True,
        null=True,
    )
    additionele_informatie = models.JSONField(default=dict)

    taak_url = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taakopdracht"
        verbose_name_plural = "Taakopdrachten"
