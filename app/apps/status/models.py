from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from utils.models import BasisModel


class Status(BasisModel):
    class NaamOpties(models.TextChoices):
        OPENSTAAND = "openstaand", "Openstaand"
        IN_BEHANDELING = "in_behandeling", "In behandeling"
        CONTROLE = "controle", "Controle"
        AFGEHANDELD = "afgehandeld", "Afgehandeld"

    naam = models.CharField(
        max_length=50,
        choices=NaamOpties.choices,
        default=NaamOpties.OPENSTAAND,
    )
    melding = models.ForeignKey(
        to="meldingen.Melding",
        related_name="statussen_voor_melding",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("-aangemaakt_op",)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.naam}({self.pk})"

    def volgende_statussen(self):
        match self.naam:
            case Status.NaamOpties.IN_BEHANDELING:
                return [
                    Status.NaamOpties.CONTROLE,
                ]
            case Status.NaamOpties.OPENSTAAND:
                return [
                    Status.NaamOpties.IN_BEHANDELING,
                    Status.NaamOpties.AFGEHANDELD,
                ]
            case Status.NaamOpties.CONTROLE:
                return [
                    Status.NaamOpties.IN_BEHANDELING,
                    Status.NaamOpties.AFGEHANDELD,
                ]
            case _:
                return []

    def status_verandering_toegestaan(self, status_naam):
        return status_naam in self.volgende_statussen()

    def clean(self):
        errors = {}
        huidige_status = self.melding.status.naam if self.melding.status else ""
        nieuwe_status = self.naam

        if nieuwe_status == huidige_status:
            error_msg = "Status verandering niet toegestaan: van `{from_state}` naar `{to_state}`.".format(
                from_state=huidige_status, to_state=nieuwe_status
            )
            errors["taakstatus"] = ValidationError(error_msg, code="invalid")

        if errors:
            raise ValidationError(errors)

    class StatusVeranderingNietToegestaan(Exception):
        pass
