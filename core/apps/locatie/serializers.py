from apps.locatie.models import Adres, Geometrie, Graf, Lichtmast
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers


class GeometrieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geometrie
        fields = (
            "bron",
            "geometrie",
        )


class AdresSerializer(WritableNestedModelSerializer):
    geometrieen = GeometrieSerializer(many=True, required=False)

    class Meta:
        model = Adres
        fields = (
            "bron",
            "plaatsnaam",
            "straatnaam",
            "huisnummer",
            "huisletter",
            "toevoeging",
            "postcode",
            "geometrieen",
        )


class GrafSerializer(WritableNestedModelSerializer):
    geometrieen = GeometrieSerializer(many=True, required=False)

    class Meta:
        model = Graf
        fields = (
            "bron",
            "plaatsnaam",
            "begraafplaats",
            "grafnummer",
            "vak",
            "geometrieen",
        )


class LichtmastSerializer(WritableNestedModelSerializer):
    geometrieen = GeometrieSerializer(many=True, required=False)

    class Meta:
        model = Lichtmast
        fields = (
            "bron",
            "lichtmast",
            "geometrieen",
        )
