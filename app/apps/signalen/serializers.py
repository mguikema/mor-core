from apps.aliassen.serializers import OnderwerpAliasSerializer
from apps.bijlagen.serializers import BijlageSerializer
from apps.locatie.models import Adres, Graf, Lichtmast
from apps.locatie.serializers import (
    AdresSerializer,
    GrafSerializer,
    LichtmastSerializer,
)
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
    graven = GrafSerializer(many=True, required=False)
    adressen = AdresSerializer(many=True, required=False)
    lichtmasten = LichtmastSerializer(many=True, required=False)
    bijlagen = BijlageSerializer(many=True, required=False)
    onderwerpen = OnderwerpAliasSerializer(many=True, required=False)

    # def create(self, validated_data):
    #     signaal = Melding.acties.aanmaken(
    #         validated_data, self.get_initial(), self.context.get("request")
    #     )
    #     return signaal

    def create(self, validated_data):
        locaties = (("adressen", Adres), ("lichtmasten", Lichtmast), ("graven", Graf))
        locaties_data = {
            loc[0]: validated_data.pop(loc[0], None)
            for loc in locaties
            if validated_data.get(loc[0])
        }
        signaal = super().create(validated_data)

        for location in locaties:
            model = location[1]
            for loc in locaties_data.get(location[0], []):
                model.objects.create(**loc, signaal=signaal)
            validated_data.pop(location[0], None)

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
        # read_only_fields = ("melding",)
