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
from apps.taken.models import Taakopdracht
from django.core.exceptions import ValidationError
from rest_framework import serializers


class TaakopdrachtSerializer(serializers.ModelSerializer):
    taaktype = serializers.URLField()

    class Meta:
        model = Taakopdracht
        fields = (
            "taaktype",
            "titel",
            "bericht",
            "additionele_informatie",
            "status",
            "taakapplicatie",
            "melding",
        )
        read_only_fields = ("status",)

    def to_internal_value(self, data):
        taakapplicatie = None
        try:
            taakapplicatie = (
                self.context.get("request")
                .user.taakapplicatie_voor_gebruiker.all()
                .first()
            )
        except Exception:
            raise Exception("Er is geen taakapplicatie gedefinieerd voor de gebruiker")
        data.update(
            {
                "taakapplicatie": taakapplicatie.id,
            }
        )
        return super().to_internal_value(data)

    def validate(self, attrs):
        validated_attrs = super().validate(attrs)
        errors = {}

        if errors:
            raise ValidationError(errors)

        return validated_attrs

    def create(self, validated_data):
        return Taakopdracht.objects.create(**validated_data)


class TaakSerializerExtern(serializers.Serializer):
    taaktype = serializers.URLField()
    melding = serializers.URLField()
    titel = serializers.CharField()
    bericht = serializers.CharField(required=False)
    additionele_informatie = serializers.JSONField(required=False)
