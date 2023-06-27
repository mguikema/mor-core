import logging
import mimetypes
import os
from os.path import exists

import pyheif
from apps.applicaties.models import Applicatie
from apps.meldingen.managers import MeldingManager
from apps.meldingen.querysets import MeldingQuerySet
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django_extensions.db.fields import AutoSlugField
from PIL import Image, UnidentifiedImageError
from sorl.thumbnail import get_thumbnail
from utils.images import get_upload_path
from utils.models import BasisModel

logger = logging.getLogger(__name__)


class Bron(BasisModel):
    naam = models.CharField(max_length=30)


class Bijlage(BasisModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    bestand = models.FileField(
        upload_to=get_upload_path, null=False, blank=False, max_length=255
    )
    afbeelding = models.ImageField(
        upload_to=get_upload_path, null=True, blank=True, max_length=255
    )
    afbeelding_verkleind = models.ImageField(
        upload_to=get_upload_path, null=True, blank=True, max_length=255
    )

    mimetype = models.CharField(max_length=30, blank=False, null=False)
    is_afbeelding = models.BooleanField(default=False)

    class BestandPadFout(Exception):
        ...

    class AfbeeldingVersiesAanmakenFout(Exception):
        ...

    def _is_afbeelding(self):
        try:
            Image.open(self.bestand)
        except UnidentifiedImageError:
            return False
        return True

    def _heic_to_jpeg(self, file_field):
        heif_file = pyheif.read(file_field.path)
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )
        new_file_name = f"{file_field.name}.jpg"
        image.save(os.path.join(settings.MEDIA_ROOT, new_file_name), "JPEG")
        return new_file_name

    def aanmaken_afbeelding_versies(self):
        logger.info("aanmaken_afbeelding_versies")
        mt = mimetypes.guess_type(self.bestand.path, strict=True)
        logger.info(mt)
        if exists(self.bestand.path):
            logger.info(mt)
            bestand = self.bestand.path
            self.is_afbeelding = self._is_afbeelding()
            if mt:
                self.mimetype = mt[0]
            if self.mimetype == "image/heic":
                bestand = self._heic_to_jpeg(self.bestand)
                self.is_afbeelding = True

            logger.info(f"is afbeelding: {self.is_afbeelding}")
            if self.is_afbeelding:
                try:
                    self.afbeelding_verkleind.name = get_thumbnail(
                        bestand,
                        settings.THUMBNAIL_KLEIN,
                        format="JPEG",
                        quality=99,
                    ).name
                    self.afbeelding.name = get_thumbnail(
                        bestand,
                        settings.THUMBNAIL_STANDAARD,
                        format="JPEG",
                        quality=80,
                    ).name
                except Exception as e:
                    raise Bijlage.AfbeeldingVersiesAanmakenFout(
                        f"aanmaken_afbeelding_versies: get_thumbnail fout: {e}"
                    )
        else:
            raise Bijlage.BestandPadFout(
                f"aanmaken_afbeelding_versies: bestand path bestaat niet, bijlage id: {self.pk}"
            )

    class Meta:
        verbose_name = "Bijlage"
        verbose_name_plural = "Bijlagen"


class MeldingGebeurtenis(BasisModel):
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
    omschrijving_extern = models.CharField(max_length=5000, null=True, blank=True)
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


class Melder(BasisModel):
    naam = models.CharField(max_length=100, blank=True, null=True)
    voornaam = models.CharField(max_length=50, blank=True, null=True)
    achternaam = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefoonnummer = models.CharField(max_length=17, blank=True, null=True)

    class Meta:
        verbose_name = "Melder"
        verbose_name_plural = "Melders"


class MeldingContext(BasisModel):
    naam = models.CharField(max_length=100)
    slug = AutoSlugField(
        populate_from=("naam",),
        blank=False,
        overwrite=True,
        editable=False,
        unique=True,
    )
    onderwerpen = models.ManyToManyField(
        to="aliassen.OnderwerpAlias",
        related_name="meldingcontexten_voor_onderwerpen",
        blank=True,
    )
    veld_waardes = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Melding context"
        verbose_name_plural = "Melding contexten"

    def __str__(self) -> str:
        return f"{self.naam}({self.pk})"

    def veld_waardes_toevoegen(self, extra_veld_waardes: dict):
        for k, v in extra_veld_waardes.items():
            if not self.veld_waardes.get(k):
                self.veld_waardes[k] = v
            else:
                self.veld_waardes[k]["label"] = v.get("label")
                choices = self.veld_waardes.get(k, {}).get("choices", {})
                extra_choices = extra_veld_waardes.get(k, {}).get("choices", {})
                if isinstance(choices, dict) and isinstance(extra_choices, dict):
                    choices.update(extra_choices)
                self.veld_waardes[k]["choices"] = choices


class Signaal(BasisModel):
    """
    Een signaal een individuele signaal vanuit de buiten ruimte.
    Er kunnen meerdere signalen aan een melding gekoppeld zijn, bijvoorbeeld dubbele signalen.
    Maar er altijd minimaal een signaal gerelateerd aan een Melding.
    Er mag binnen deze applicatie geen extra info over een signaal

    Het verwijzing veld, moet nog nader bepaald worden. Vermoedelijk wordt dit een url
    """

    signaal_url = models.URLField()
    signaal_data = models.JSONField(default=dict)
    melder = models.OneToOneField(
        to="meldingen.Melder", on_delete=models.SET_NULL, null=True, blank=True
    )
    melding = models.ForeignKey(
        to="meldingen.Melding",
        related_name="signalen_voor_melding",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    def notificatie_melding_afgesloten(self):
        applicatie = Applicatie.vind_applicatie_obv_uri(self.signaal_url)
        applicatie.notificatie_melding_afgesloten(self.signaal_url)

    class Meta:
        verbose_name = "Signaal"
        verbose_name_plural = "Signalen"


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
