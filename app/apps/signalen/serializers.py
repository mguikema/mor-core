from apps.bijlagen.serializers import BijlageSerializer
from apps.locatie.serializers import (
    AdresBasisSerializer,
    GrafBasisSerializer,
    LichtmastBasisSerializer,
)
from apps.melders.serializers import MelderSerializer
from apps.meldingen.models import Melding
from apps.signalen.models import Signaal
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.reverse import reverse


class SignaalLinksSerializer(serializers.Serializer):
    self = serializers.SerializerMethodField()
    melding = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.URI)
    def get_self(self, obj):
        return reverse(
            "v1:signaal-detail",
            kwargs={"uuid": obj.uuid},
            request=self.context.get("request"),
        )

    @extend_schema_field(OpenApiTypes.URI)
    def get_melding(self, obj):
        return reverse(
            "v1:melding-detail",
            kwargs={"uuid": obj.melding.uuid},
            request=self.context.get("request"),
        )


class SignaalSerializer(WritableNestedModelSerializer):
    _links = SignaalLinksSerializer(source="*", read_only=True)
    bijlagen = BijlageSerializer(many=True, required=False, write_only=True)
    melder = MelderSerializer(required=False, write_only=True)
    omschrijving_kort = serializers.CharField(max_length=500, write_only=True)
    omschrijving = serializers.CharField(
        max_length=5000, allow_blank=True, required=False, write_only=True
    )
    meta = serializers.JSONField(default=dict, write_only=True)
    meta_uitgebreid = serializers.JSONField(default=dict, write_only=True)
    adressen = AdresBasisSerializer(many=True, required=False, write_only=True)
    lichtmasten = LichtmastBasisSerializer(many=True, required=False, write_only=True)
    graven = GrafBasisSerializer(many=True, required=False, write_only=True)
    origineel_aangemaakt = serializers.DateTimeField(write_only=True)
    onderwerpen = serializers.ListSerializer(
        child=serializers.URLField(), write_only=True
    )

    def create(self, validated_data):
        signaal = Melding.acties.aanmaken(
            validated_data, self.get_initial(), self.context.get("request")
        )
        return signaal

    class Meta:
        model = Signaal
        fields = (
            "_links",
            "uuid",
            "signaal_url",
            "signaal_data",
            "origineel_aangemaakt",
            "omschrijving_kort",
            "omschrijving",
            "meta",
            "meta_uitgebreid",
            "onderwerpen",
            "bijlagen",
            "melder",
            "adressen",
            "lichtmasten",
            "graven",
            "melding",
        )
        read_only_fields = ("melding",)
