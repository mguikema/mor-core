import filetype
from apps.aliassen.serializers import OnderwerpAliasSerializer
from apps.locatie.serializers import (
    AdresSerializer,
    GeometrieSerializer,
    GrafRelatedField,
    GrafSerializer,
    LichtmastSerializer,
    LocatieRelatedField,
)
from apps.meldingen.models import (
    Bijlage,
    Melder,
    Melding,
    MeldingContext,
    MeldingGebeurtenis,
    Signaal,
)
from apps.status.serializers import StatusSerializer
from drf_extra_fields.fields import Base64FileField
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers


class DefaultBase64File(Base64FileField):
    ALLOWED_TYPES = ["jpg", "jpeg", "png", "rtf", "doc", "docx", "heic"]

    def get_file_extension(self, filename, decoded_file):
        kind = filetype.guess(decoded_file)
        return kind.extension


class BijlageSerializer(serializers.ModelSerializer):
    """
    Bijlage comment van serializer
    """

    bestand = DefaultBase64File()
    afbeelding_relative_url = serializers.SerializerMethodField()
    afbeelding_verkleind_relative_url = serializers.SerializerMethodField()

    def get_afbeelding_relative_url(self, obj):
        return obj.afbeelding.url if obj.afbeelding else None

    def get_afbeelding_verkleind_relative_url(self, obj):
        return obj.afbeelding_verkleind.url if obj.afbeelding_verkleind else None

    class Meta:
        model = Bijlage
        fields = (
            "bestand",
            "afbeelding",
            "afbeelding_relative_url",
            "mimetype",
            "is_afbeelding",
            "bestand_relative_url",
            "afbeelding_verkleind_relative_url",
        )
        read_only_fields = (
            "afbeelding",
            "afbeelding_verkleind",
            "is_afbeelding",
            "mimetype",
            "afbeelding_relative_url",
            "afbeelding_verkleind_relative_url",
        )


class BijlageRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        serializer = BijlageSerializer(value, context=self.context)
        return serializer.data


class MelderSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Melder
        fields = (
            "naam",
            "voornaam",
            "achternaam",
            "email",
            "telefoonnummer",
        )


class MeldingGebeurtenisStatusSerializer(WritableNestedModelSerializer):
    bijlagen = BijlageSerializer(many=True, required=False)
    status = StatusSerializer(required=True)
    gebeurtenis_type = serializers.CharField(required=False)
    resolutie = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = MeldingGebeurtenis
        fields = (
            "aangemaakt_op",
            "gebeurtenis_type",
            "bijlagen",
            "status",
            "resolutie",
            "omschrijving_intern",
            "omschrijving_extern",
            "melding",
        )
        read_only_fields = ("aangemaakt_op",)


class MeldingGebeurtenisSerializer(WritableNestedModelSerializer):
    bijlagen = BijlageSerializer(many=True, required=False)
    status = StatusSerializer(required=False)

    class Meta:
        model = MeldingGebeurtenis
        fields = (
            "aangemaakt_op",
            "gebeurtenis_type",
            "bijlagen",
            "status",
            "omschrijving_intern",
            "omschrijving_extern",
            "melding",
        )
        read_only_fields = (
            "aangemaakt_op",
            "gebeurtenis_type",
            "status",
        )
        validators = []


class SignaalSerializer(WritableNestedModelSerializer):
    bijlagen = BijlageSerializer(many=True, required=False)
    melder = MelderSerializer(required=False)

    class Meta:
        model = Signaal
        fields = (
            "origineel_aangemaakt",
            "onderwerpen",
            "ruwe_informatie",
            "bijlagen",
            "bron",
            "melder",
        )


class MeldingContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeldingContext
        lookup_field = "slug"
        fields = "__all__"


class MeldingSerializer(serializers.ModelSerializer):
    locaties_voor_melding = LocatieRelatedField(many=True, read_only=True)
    bijlagen = BijlageRelatedField(many=True, read_only=True)
    status = StatusSerializer()
    volgende_statussen = serializers.ListField(
        source="status.volgende_statussen",
        child=serializers.CharField(),
        read_only=True,
    )

    class Meta:
        model = Melding
        fields = (
            "id",
            "uuid",
            "aangemaakt_op",
            "aangepast_op",
            "origineel_aangemaakt",
            "afgesloten_op",
            "omschrijving_kort",
            "meta",
            "onderwerpen",
            "bijlagen",
            "locaties_voor_melding",
            "status",
            "resolutie",
            "volgende_statussen",
        )


class MeldingDetailSerializer(MeldingSerializer):
    locaties_voor_melding = LocatieRelatedField(many=True, read_only=True)
    onderwerpen = OnderwerpAliasSerializer(many=True, read_only=True)
    bijlagen = BijlageRelatedField(many=True, read_only=True)
    status = StatusSerializer()
    volgende_statussen = serializers.ListField(
        source="status.volgende_statussen",
        child=serializers.CharField(),
        read_only=True,
    )
    melding_gebeurtenissen = MeldingGebeurtenisSerializer(many=True, read_only=True)
    taakapplicaties = serializers.SerializerMethodField()

    def get_taakapplicaties(self, obj):
        from apps.applicaties.models import Taakapplicatie

        self.context.get("request").user.taakapplicatie_voor_gebruiker.all()
        taakapplicaties = Taakapplicatie.objects.filter(
            onderwerpen__in=obj.onderwerpen.all()
        ).distinct()

        return taakapplicaties.values_list("naam", flat=True)

    class Meta:
        model = Melding
        fields = (
            "id",
            "uuid",
            "aangemaakt_op",
            "aangepast_op",
            "origineel_aangemaakt",
            "afgesloten_op",
            "omschrijving",
            "omschrijving_kort",
            "meta",
            "meta_uitgebreid",
            "onderwerpen",
            "bijlagen",
            "locaties_voor_melding",
            "status",
            "resolutie",
            "volgende_statussen",
            "melding_gebeurtenissen",
            "taakapplicaties",
        )
