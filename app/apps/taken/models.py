from apps.bijlagen.models import Bijlage
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from rest_framework.exceptions import APIException
from utils.fields import DictJSONField
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
    additionele_informatie = DictJSONField(default=dict)

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taakgebeurtenis"
        verbose_name_plural = "Taakgebeurtenissen"


class Taakstatus(BasisModel):
    class NaamOpties(models.TextChoices):
        NIEUW = "nieuw", "Nieuw"
        TOEGEWEZEN = "toegewezen", "Toegewezen"
        OPENSTAAND = "openstaand", "Openstaand"
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
                    Taakstatus.NaamOpties.TOEGEWEZEN,
                    Taakstatus.NaamOpties.VOLTOOID,
                ]
            case Taakstatus.NaamOpties.TOEGEWEZEN:
                return [
                    Taakstatus.NaamOpties.OPENSTAAND,
                    Taakstatus.NaamOpties.VOLTOOID,
                ]
            case Taakstatus.NaamOpties.OPENSTAAND:
                return [
                    Taakstatus.NaamOpties.TOEGEWEZEN,
                    Taakstatus.NaamOpties.VOLTOOID,
                ]
            case _:
                return []

    def clean(self):
        huidige_status = (
            self.taakopdracht.status.naam if self.taakopdracht.status else ""
        )
        nieuwe_status = self.naam
        if huidige_status == nieuwe_status:
            raise Taakstatus.TaakStatusVeranderingNietToegestaan(
                "De nieuwe taakstatus mag niet hezelfde zijn als de huidige"
            )

    class TaakStatusVeranderingNietToegestaan(APIException):
        pass

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


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
        NIET_GEVONDEN = "niet_gevonden", "Niets aangetroffen"

    afgesloten_op = models.DateTimeField(null=True, blank=True)
    afhandeltijd = models.DurationField(null=True, blank=True)
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
    additionele_informatie = DictJSONField(default=dict)

    taak_url = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )

    class AanmakenNietToegestaan(APIException):
        ...

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Taakopdracht"
        verbose_name_plural = "Taakopdrachten"

    def clean(self):
        if self.pk is None:
            status_namen = [
                status_naam[0]
                for status_naam in Taakstatus.NaamOpties.choices
                if Taakstatus.NaamOpties.VOLTOOID != status_naam[0]
            ]
            openstaande_taken = self.melding.taakopdrachten_voor_melding.filter(
                status__naam__in=status_namen
            )
            gebruikte_taaktypes = list(
                {
                    taaktype
                    for taaktype in openstaande_taken.values_list("taaktype", flat=True)
                    .order_by("taaktype")
                    .distinct()
                }
            )
            if self.taaktype in gebruikte_taaktypes:
                raise Taakopdracht.AanmakenNietToegestaan(
                    "Er is al een taakopdracht met dit taaktype voor deze melding"
                )

    def save(self, *args, **kwargs):
        if self.afgesloten_op and self.aangemaakt_op:
            self.afhandeltijd = self.afgesloten_op - self.aangemaakt_op
        else:
            self.afhandeltijd = None
        self.full_clean()
        return super().save(*args, **kwargs)
