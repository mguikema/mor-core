import mimetypes
import os
from os.path import exists

import pyheif
import requests
from apps.mor.managers import MeldingManager
from apps.mor.querysets import MeldingQuerySet, SignaalQuerySet
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django_extensions.db.fields import AutoSlugField
from PIL import Image, UnidentifiedImageError
from sorl.thumbnail import get_thumbnail
from utils.images import get_upload_path
from utils.models import BasisModel


class Bron(BasisModel):
    naam = models.CharField(max_length=30)


class Bijlage(BasisModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    bestand = models.FileField(
        upload_to=get_upload_path, null=False, blank=False, max_length=255
    )
    afbeelding_verkleind = models.ImageField(
        upload_to=get_upload_path, null=True, blank=True, max_length=255
    )

    mimetype = models.CharField(max_length=30, blank=False, null=False)
    is_afbeelding = models.BooleanField(default=False)

    def _is_afbeelding(self):
        try:
            Image.open(self.bestand)
        except UnidentifiedImageError:
            return False
        return True

    def _heic_to_jpeg(self, file_field):
        heif_file = pyheif.read(file_field)
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

    def save(self, *args, **kwargs):
        if self.pk is None:
            mt = mimetypes.guess_type(self.bestand.path, strict=True)
            if exists(self.bestand.path):
                if mt:
                    self.mimetype = mt[0]
                if self.mimetype == "image/heic":
                    self.bestand = self._heic_to_jpeg(self.bestand)
                self.is_afbeelding = self._is_afbeelding()
                if self.is_afbeelding:
                    im = get_thumbnail(
                        self.bestand.path,
                        settings.THUMBNAIL_KLEIN,
                        crop="center",
                        quality=99,
                    )
                    self.afbeelding_verkleind.name = im.name

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Bijlage"
        verbose_name_plural = "Bijlagen"


class TaakApplicatie(BasisModel):
    """
    Representeerd externe applicaite die de afhandling van de melden op zich nemen.
    """

    naam = models.CharField(
        max_length=100,
        default="Taak applicatie",
    )


class MeldingGebeurtenisType(BasisModel):
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


class MeldingGebeurtenis(BasisModel):
    """
    MeldingGebeurtenissen bouwen de history op van van de melding
    """

    bijlagen = GenericRelation(Bijlage)
    status = models.OneToOneField(
        to="status.Status",
        related_name="melding_gebeurtenis_voor_status",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    omschrijving = models.CharField(max_length=5000, null=True, blank=True)
    melding = models.ForeignKey(
        to="mor.Melding",
        related_name="melding_gebeurtenissen",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Melding gebeurtenis"
        verbose_name_plural = "Melding gebeurtenissen"


class OnderwerpAlias(BasisModel):
    bron_url = models.CharField(max_length=500)
    response_json = models.JSONField(
        default=dict,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Onderwerp alias"
        verbose_name_plural = "Onderwerp aliassen"

    class OnderwerpNietValide(Exception):
        pass

    def _valideer_bron_url(self, bron_url: str):
        response = requests.get(bron_url)
        if response.status_code != 200:
            raise OnderwerpAlias.OnderwerpNietValide
        return response.json()

    def save(self, *args, **kwargs):
        self.response_json = self._valideer_bron_url(self.bron_url)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        try:
            return self.response_json.get("naam", self.bron_url)
        except Exception:
            return self.bron_url


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
        to="mor.OnderwerpAlias",
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


class MeldingBasis(BasisModel):
    origineel_aangemaakt = models.DateTimeField()
    onderwerp = models.CharField(max_length=300)

    """
    TODO: Er is behoefte aan opslag van extra info. De structuur hiervan zou kunnen afhangen van het onderwerp van de melding of de bron(b.v. melder applicatie)
    Voor nu ongestructureerde json data.
    """

    bijlagen = GenericRelation(Bijlage)

    class Meta:
        abstract = True


class Signaal(MeldingBasis):
    """
    Een signaal een individuele signaal vanuit de buiten ruimte.
    Er kunnen meerdere signalen aan een melding gekoppeld zijn, bijvoorbeeld dubbele signalen.
    Maar er altijd minimaal een signaal gerelateerd aan een Melding.
    Er mag binnen deze applicatie geen extra info over een signaal

    Het verwijzing veld, moet nog nader bepaald worden. Vermoedelijk wordt dit een url
    """

    bron = models.CharField(max_length=200)
    onderwerpen = ArrayField(base_field=models.CharField(max_length=300), default=list)
    melder = models.OneToOneField(
        to="mor.Melder", on_delete=models.SET_NULL, null=True, blank=True
    )
    ruwe_informatie = models.JSONField(default=dict)
    melding = models.ForeignKey(
        to="mor.Melding",
        related_name="signalen_voor_melding",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    objects = SignaalQuerySet.as_manager()

    class Meta:
        verbose_name = "Signaal"
        verbose_name_plural = "Signalen"


class Melding(MeldingBasis):
    """
    Een melding is de ontdubbelde versie van signalen
    """

    """
    Als er geen taak_applicaties zijn linked aan deze melding, kan b.v. MidOffice deze handmatig toewijzen
    """
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
    onderwerpen = models.ManyToManyField(
        to="mor.OnderwerpAlias",
        related_name="meldingen_voor_onderwerpen",
        blank=True,
    )
    melding_context = models.ForeignKey(
        to="mor.MeldingContext",
        related_name="meldingen_voor_meldingcontext",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    objects = MeldingQuerySet.as_manager()
    acties = MeldingManager()

    class Meta:
        verbose_name = "Melding"
        verbose_name_plural = "Meldingen"
