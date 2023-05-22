from apps.meldingen.models import Bijlage
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
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
    taakopdracht = models.ForeignKey(
        to="taken.Taakopdracht",
        related_name="taakgebeurtenissen_voor_taakopdracht",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("-aangemaakt_op",)
        verbose_name = "Melding gebeurtenis"
        verbose_name_plural = "Melding gebeurtenissen"


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

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.naam}({self.pk})"

    def clean(self):
        errors = {}
        huidige_status = (
            self.taakopdracht.status.naam if self.taakopdracht.status else ""
        )
        nieuwe_status = self.naam

        if nieuwe_status == huidige_status:
            error_msg = "Status verandering niet toegestaan: van `{from_state}` naar `{to_state}`.".format(
                from_state=huidige_status, to_state=nieuwe_status
            )
            errors["taakstatus"] = ValidationError(error_msg, code="invalid")

        if errors:
            raise ValidationError(errors)

    class TaakStatusVeranderingNietToegestaan(Exception):
        pass


class Taakopdracht(BasisModel):
    """
    Taakapplicaties kunnen een taakopdracht aanmaken in more-core.
    Op basis van de taakopdracht wordt er een taak aangemaakt in een taakapplicatie.
    In de response zit de taak_url, die weer opgeslagen wordt in deze taakopdracht.
    Zo worden taakopdrachten aan taken gelinked.
    """

    melding = models.ForeignKey(
        to="meldingen.Melding",
        related_name="taakopdrachten_voor_melding",
        on_delete=models.CASCADE,
    )
    taakapplicatie = models.ForeignKey(
        to="applicaties.Taakapplicatie",
        related_name="taakopdrachten_voor_taakapplicatie",
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
    # laatst_ontvangen_update = models.DateTimeField()
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
