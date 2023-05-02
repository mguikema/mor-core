from apps.locatie.models import Adres, Geometrie, Graf, Lichtmast, Locatie
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers


class GeometrieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geometrie
        fields = (
            "bron",
            "geometrie",
        )


class LocatieSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Locatie
        fields = "__all__"


class LocatieRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        serializer = LocatieSerializer(value)
        return serializer.data


class AdresSerializer(WritableNestedModelSerializer):
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
            "geometrie",
        )


class GrafSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Graf
        fields = (
            "bron",
            "plaatsnaam",
            "begraafplaats",
            "grafnummer",
            "vak",
            "geometrie",
        )


class LichtmastSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Lichtmast
        fields = (
            "bron",
            "lichtmast_id",
            "geometrie",
        )


class GrafRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        serializer = GrafSerializer(value)
        return serializer.data
