import mimetypes

from apps.locatie.models import Adres, Geometrie, Graf, Lichtmast
from apps.mor.querysets import MeldingQuerySet, SignaalQuerySet
from box import Box
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from PIL import Image, UnidentifiedImageError
from utils.models import BasisModel


class Bron(BasisModel):
    naam = models.CharField(max_length=30)


class Bijlage(BasisModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
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
            mt = mimetypes.guess_type(self.bestand.path, strict=True)
            if mt:
                self.mimetype = mt[0]

        super().save(*args, **kwargs)


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

    bijlages = GenericRelation(Bijlage)
    melding = models.ForeignKey(
        to="mor.Melding",
        related_name="melding_gebeurtenissen",
        on_delete=models.CASCADE,
    )


class Melder(BasisModel):
    naam = models.CharField(max_length=100, blank=True, null=True)
    voornaam = models.CharField(max_length=50, blank=True, null=True)
    achternaam = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefoonnummer = models.CharField(max_length=17, blank=True, null=True)


class MeldingBasis(BasisModel):
    origineel_aangemaakt = models.DateTimeField()
    tekst = models.CharField(max_length=3000)
    onderwerp = models.CharField(max_length=300)

    """
    TODO: Er is behoefte aan opslag van extra info. De structuur hiervan zou kunnen afhangen van het onderwerp van de melding of de bron(b.v. melder applicatie)
    Voor nu ongestructureerde json data.
    """
    meta = models.JSONField(default=dict)

    bijlagen = GenericRelation(Bijlage)
    geometrieen = GenericRelation(Geometrie)
    adressen = GenericRelation(Adres)
    graven = GenericRelation(Graf)
    lichtmasten = GenericRelation(Lichtmast)

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

    melder = models.OneToOneField(
        to="mor.Melder", on_delete=models.SET_NULL, null=True, blank=True
    )
    bron = models.CharField(max_length=300)
    melding = models.ForeignKey(
        to="mor.Melding",
        related_name="signalen_voor_melding",
        on_delete=models.CASCADE,
        null=True,
    )
    objects = SignaalQuerySet.as_manager()

    def parse_querystring(self, qs_template, **kwargs):
        format_data = {
            "aangemaakt": self.aangemaakt_op,
            "origineel_aangemaakt": self.origineel_aangemaakt,
            "tekst": self.tekst,
            "meta": Box(**self.meta),
            "bron": self.bron,
            "melder": self.melder,
        }
        try:
            qs_template.format(**format_data)
        except Exception as e:
            print(e)
        return qs_template.format(**format_data)


class Melding(MeldingBasis):
    """
    Een melding is de ontdubbelde versie van signalen
    """

    """
    Als er geen taak_applicaties zijn linked aan deze melding, kan b.v. MidOffice deze handmatig toewijzen
    """
    afgesloten_op = models.DateTimeField(null=True, blank=True)
    taak_applicaties = models.ManyToManyField(
        to="mor.TaakApplicatie",
        related_name="meldingen",
        blank=True,
    )
    objects = MeldingQuerySet.as_manager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
