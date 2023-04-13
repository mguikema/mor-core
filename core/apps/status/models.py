from apps.status import workflow
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from utils.models import BasisModel


class Status(BasisModel):
    naam = models.CharField(
        max_length=50,
        blank=True,
        choices=workflow.STATUS_CHOICES,
        default=workflow.GEMELD,
        help_text="Melding status",
    )
    melding = models.ForeignKey(
        to="mor.Melding",
        related_name="statussen_voor_melding",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("-aangemaakt_op",)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def volgende_statussen(self):
        return workflow.ALLOWED_STATUS_CHANGES[self.naam]

    def clean(self):
        errors = {}
        if self.melding.status:
            huidige_status = self.melding.status.naam
        else:
            huidige_status = workflow.LEEG

        nieuwe_status = self.naam

        # Validating state transition.
        if nieuwe_status not in workflow.ALLOWED_STATUS_CHANGES[huidige_status]:
            error_msg = (
                "Invalid state transition from `{from_state}` to `{to_state}`.".format(
                    from_state=huidige_status, to_state=nieuwe_status
                )
            )
            errors["status"] = ValidationError(error_msg, code="invalid")

        if errors:
            raise ValidationError(errors)
