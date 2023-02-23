from django.contrib.gis.db import models
from PIL import Image, UnidentifiedImageError


class Bijlage(models.Model):
    melding_gebeurtenis = models.ForeignKey(
        to="mor.MeldingGebeurtenis",
        related_name="bijlages",
        on_delete=models.CASCADE,
    )
    bestand = models.FileField(
        upload_to="attachments/%Y/%m/%d/", null=False, blank=False, max_length=255
    )
    mimetype = models.CharField(max_length=30, blank=False, null=False)
    is_afbeelding = models.BooleanField(default=False)

    def _is_afbeelding(self):
        try:
            Image.open(self.bestand)
        except UnidentifiedImageError:
            return False
        return True

    def save(self, *args, **kwargs):
        if self.pk is None:
            # Check of het bestand een afbeelding is
            self.is_afbeelding = self._is_afbeelding()

            if not self.mimetype and hasattr(self.bestand.file, "content_type"):
                self.mimetype = self.bestand.file.content_type

        super().save(*args, **kwargs)


class TaakApplicatie(models.Model):
    """
    Representeerd externe applicaite die de afhandling van de melden op zich nemen.
    """

    naam = models.CharField(
        max_length=100,
        default="Taak applicatie",
    )


class MeldingGebeurtenisType(models.Model):
    class TypeNaamOpties(models.TextChoices):
        META_DATA_WIJZIGING = "META_DATA_WIJZIGING", "Meta data wijziging"
        STATUS_WIJZIGING = "STATUS_WIJZIGING", "Status change"

    type_naam = models.CharField(
        max_length=50,
        choices=TypeNaamOpties.choices,
    )
    melding_gebeurtenis = models.ForeignKey(
        to="mor.MeldingGebeurtenis",
        related_name="melding_gebeurtenistypes",
        on_delete=models.CASCADE,
    )
    meta = models.JSONField(default=dict)


class MeldingGebeurtenis(models.Model):
    """
    MeldingGebeurtenissen bouwen de history op van van de melding
    """

    aangemaakt = models.DateTimeField(auto_now_add=True)
    melding = models.ForeignKey(
        to="mor.Melding",
        related_name="melding_gebeurtenissen",
        on_delete=models.CASCADE,
    )


class Geometrie(models.Model):
    """
    Basis klasse voor geo info.
    """

    geometrie = models.GeometryField()
    meta = models.JSONField(default=dict)
    melding = models.ForeignKey(
        to="mor.Melding",
        related_name="geometrieen",
        on_delete=models.CASCADE,
        null=True,
    )


class Signaal(models.Model):
    """
    Een signaal een individuele signaal vanuit de buiten ruimte.
    Er kunnen meerdere signalen aan een melding gekoppeld zijn, bijvoorbeeld dubbele signalen.
    Maar er altijd minimaal een signaal gerelateerd aan een Melding.
    Er mag binnen deze applicatie geen extra info over een signaal

    Het verwijzing veld, moet nog nader bepaald worden. Vermoedelijk wordt dit een url
    """

    verwijzing = models.TextField()
    melding = models.ForeignKey(
        to="mor.Melding", related_name="signalen", on_delete=models.CASCADE, null=True
    )


class Melding(models.Model):
    """
    Een melding is de ontdubbelde versie van signalen
    """

    aangemaakt = models.DateTimeField(auto_now_add=True)

    """
    If the incident_handler field is empty, no one is responsable for the melding
    Maybe an orchestrator like  MidOffice can be connected automaticaly


    """
    taak_applicaties = models.ManyToManyField(
        to="mor.TaakApplicatie",
        related_name="meldingen",
        blank=True,
    )
