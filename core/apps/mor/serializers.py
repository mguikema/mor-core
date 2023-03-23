import filetype
from apps.locatie.serializers import (
    AdresSerializer,
    GeometrieSerializer,
    GrafRelatedField,
    GrafSerializer,
    LichtmastSerializer,
)
from apps.mor.models import (
    Bijlage,
    Melder,
    Melding,
    MeldingGebeurtenis,
    MeldingGebeurtenisType,
    Signaal,
    TaakApplicatie,
)
from drf_extra_fields.fields import Base64FileField
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers


class DefaultBase64File(Base64FileField):
    ALLOWED_TYPES = ["jpg", "rtf", "doc"]

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
            "mimetype",
            "is_afbeelding",
        )
        read_only_fields = (
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
    class Meta:
        model = MeldingGebeurtenis
        fields = "__all__"


class SignaalSerializer(WritableNestedModelSerializer):
    melder = MelderSerializer()
    bijlagen = BijlageSerializer(many=True, required=False)
    graven = GrafSerializer(many=True, required=False)
    # geometrieen = GeometrieSerializer(many=True, required=False)
    # adressen = AdresSerializer(many=True, required=False)
    # lichtmasten = LichtmastSerializer(many=True, required=False)

    class Meta:
        model = Signaal
        fields = (
            "melder",
            "origineel_aangemaakt",
            "tekst",
            "meta",
            "onderwerp",
            "bron",
            "bijlagen",
            "graven",
            # "geometrieen",
            # "adressen",
            # "lichtmasten",
        )


class MeldingSerializer(serializers.ModelSerializer):
    graven = GrafRelatedField(many=True, read_only=True)
    bijlagen = BijlageRelatedField(many=True, read_only=True)

    class Meta:
        model = Melding
        fields = (
            "id",
            "uuid",
            "aangemaakt_op",
            "aangepast_op",
            "origineel_aangemaakt",
            "afgesloten_op",
            "tekst",
            "meta",
            "onderwerp",
            "bijlagen",
            "graven",
        )


class MeldingDetailSerializer(MeldingSerializer):
    graven = GrafRelatedField(many=True, read_only=True)

    class Meta:
        model = Melding
        fields = (
            "id",
            "uuid",
            "aangemaakt_op",
            "aangepast_op",
            "origineel_aangemaakt",
            "tekst",
            "onderwerp",
            "graven",
        )
