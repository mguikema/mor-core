import filetype
from apps.locatie.serializers import (
    AdresSerializer,
    GeometrieSerializer,
    GrafRelatedField,
    GrafSerializer,
    LichtmastSerializer,
    LocatieRelatedField,
)
from apps.mor.models import (
    Bijlage,
    Melder,
    Melding,
    MeldingContext,
    MeldingGebeurtenis,
    MeldingGebeurtenisType,
    Signaal,
    TaakApplicatie,
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

    class Meta:
        model = Bijlage
        fields = (
            "bestand",
            "afbeelding_verkleind",
            "mimetype",
            "is_afbeelding",
        )
        read_only_fields = (
            "afbeelding_verkleind",
            "is_afbeelding",
            "mimetype",
        )


class BijlageRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        serializer = BijlageSerializer(value)
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


class TaakApplicatieSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaakApplicatie
        fields = "__all__"


class MeldingGebeurtenisTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeldingGebeurtenisType
        fields = "__all__"


class MeldingGebeurtenisSerializer(serializers.ModelSerializer):
    bijlagen = BijlageSerializer(many=True, required=False)
    status = StatusSerializer(required=False)

    class Meta:
        model = MeldingGebeurtenis
        fields = (
            "bijlagen",
            "status",
            "omschrijving",
        )


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
            "volgende_statussen",
        )


class MeldingDetailSerializer(MeldingSerializer):
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
            "volgende_statussen",
        )
