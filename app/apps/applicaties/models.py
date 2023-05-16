from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from utils.models import BasisModel


class Taakapplicatie(BasisModel):
    """
    Representeerd externe applicaite die de afhandling van de melden op zich nemen.
    """

    naam = models.CharField(
        max_length=100,
        default="Taakapplicatie",
    )
    gebruiker = models.ForeignKey(
        to=get_user_model(),
        related_name="taakapplicatie_voor_gebruiker",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    melding_context = models.ForeignKey(
        to="meldingen.MeldingContext",
        related_name="taakapplicatie_voor_melding_context",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
