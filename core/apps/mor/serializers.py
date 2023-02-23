from apps.mor.models import (
    Bijlage,
    Geometrie,
    Melding,
    MeldingGebeurtenis,
    MeldingGebeurtenisType,
    Signaal,
    TaakApplicatie,
)
from rest_framework import serializers


class BijlageSerializer(serializers.ModelSerializer):
    bestand = serializers.FileField()

    class Meta:
        model = Bijlage
        fields = (
            "bestand",
            "melding_gebeurtenis",
            "mimetype",
            "is_afbeelding",
        )
        read_only_fields = (
            "is_afbeelding",
            "mimetype",
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


class GeometrieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geometrie
        fields = "__all__"


class SignaalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signaal
        fields = "__all__"


class MeldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Melding
        fields = "__all__"
