from apps.aliassen.serializers import OnderwerpAliasSerializer
from apps.bijlagen.serializers import BijlageSerializer
from apps.locatie.models import Adres, Graf, Lichtmast
from apps.locatie.serializers import (
    AdresBasisSerializer,
    AdresSerializer,
    GeometrieSerializer,
    GrafBasisSerializer,
    GrafSerializer,
    LichtmastBasisSerializer,
    LichtmastSerializer,
    LocatieRelatedField,
)
from apps.meldingen.models import Melding, Meldinggebeurtenis
from apps.signalen.serializers import SignaalSerializer
from apps.status.serializers import StatusSerializer
from apps.taken.serializers import TaakgebeurtenisSerializer, TaakopdrachtSerializer
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.reverse import reverse


class MeldingLinksSerializer(serializers.Serializer):
    self = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.URI)
    def get_self(self, obj):
        return reverse(
            "v1:melding-detail",
            kwargs={"uuid": obj.uuid},
            request=self.context.get("request"),
        )


class BijlageRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        serializer = BijlageSerializer(value, context=self.context)
        return serializer.data


class MeldingGebeurtenisLinksSerializer(serializers.Serializer):
    self = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.URI)
    def get_self(self, obj):
        return reverse(
            "v1:meldinggebeurtenis-detail",
            kwargs={"uuid": obj.uuid},
            request=self.context.get("request"),
        )


class MeldingGebeurtenisStatusSerializer(WritableNestedModelSerializer):
    bijlagen = BijlageSerializer(many=True, required=False)
    status = StatusSerializer(required=True)
    gebeurtenis_type = serializers.CharField(required=False)
    resolutie = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Meldinggebeurtenis
        fields = (
            "aangemaakt_op",
            "gebeurtenis_type",
            "bijlagen",
            "status",
            "resolutie",
            "omschrijving_intern",
            "omschrijving_extern",
            "melding",
            "gebruiker",
        )
        read_only_fields = ("aangemaakt_op",)


class MeldinggebeurtenisSerializer(WritableNestedModelSerializer):
    _links = MeldingGebeurtenisLinksSerializer(source="*", read_only=True)
    bijlagen = BijlageSerializer(many=True, required=False)
    status = StatusSerializer(required=False)
    taakgebeurtenis = TaakgebeurtenisSerializer(required=False)

    class Meta:
        model = Meldinggebeurtenis
        fields = (
            "_links",
            "aangemaakt_op",
            "gebeurtenis_type",
            "bijlagen",
            "status",
            "omschrijving_intern",
            "omschrijving_extern",
            "melding",
            "taakgebeurtenis",
            "gebruiker",
        )
        read_only_fields = (
            "_links",
            "aangemaakt_op",
            "gebeurtenis_type",
            "status",
            "melding",
            "taakgebeurtenis",
        )
        validators = []


class MeldingAanmakenSerializer(WritableNestedModelSerializer):
    graven = GrafSerializer(many=True, required=False)
    adressen = AdresSerializer(many=True, required=False)
    lichtmasten = LichtmastSerializer(many=True, required=False)
    bijlagen = BijlageSerializer(many=True, required=False)
    onderwerpen = OnderwerpAliasSerializer(many=True, required=False)

    class Meta:
        model = Melding
        fields = (
            "origineel_aangemaakt",
            "omschrijving_kort",
            "omschrijving",
            "meta",
            "meta_uitgebreid",
            "onderwerpen",
            "bijlagen",
            "graven",
            "adressen",
            "lichtmasten",
        )

    def create(self, validated_data):
        locaties = (("adressen", Adres), ("lichtmasten", Lichtmast), ("graven", Graf))
        locaties_data = {
            loc[0]: validated_data.pop(loc[0], None)
            for loc in locaties
            if validated_data.get(loc[0])
        }
        melding = super().create(validated_data)

        for location in locaties:
            model = location[1]
            for loc in locaties_data.get(location[0], []):
                model.objects.create(**loc, melding=melding)
            validated_data.pop(location[0], None)

        return melding


class MeldingSerializer(serializers.ModelSerializer):
    _links = MeldingLinksSerializer(source="*", read_only=True)
    locaties_voor_melding = LocatieRelatedField(many=True, read_only=True)
    bijlagen = BijlageRelatedField(many=True, read_only=True)
    status = StatusSerializer(read_only=True)
    volgende_statussen = serializers.ListField(
        source="status.volgende_statussen",
        child=serializers.CharField(),
        read_only=True,
    )
    aantal_actieve_taken = serializers.SerializerMethodField()
    meldingsnummer_lijst = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.INT)
    def get_aantal_actieve_taken(self, obj):
        return obj.actieve_taakopdrachten().count()

    def get_meldingsnummer_lijst(self, obj):
        return [
            signaal.signaal_data.get("meta", {}).get("meldingsnummerField")
            for signaal in obj.signalen_voor_melding.all()
        ]

    class Meta:
        model = Melding
        fields = (
            "_links",
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
            "aantal_actieve_taken",
            "meldingsnummer_lijst",
        )


class MeldingDetailSerializer(MeldingSerializer):
    _links = MeldingLinksSerializer(source="*", read_only=True)
    locaties_voor_melding = LocatieRelatedField(many=True, read_only=True)
    onderwerpen = OnderwerpAliasSerializer(many=True, read_only=True)
    bijlagen = BijlageRelatedField(many=True, read_only=True)
    status = StatusSerializer()
    volgende_statussen = serializers.ListField(
        source="status.volgende_statussen",
        child=serializers.CharField(),
        read_only=True,
    )
    meldinggebeurtenissen = MeldinggebeurtenisSerializer(
        source="meldinggebeurtenissen_voor_melding", many=True, read_only=True
    )
    taakopdrachten_voor_melding = TaakopdrachtSerializer(many=True, read_only=True)
    signalen_voor_melding = SignaalSerializer(many=True, read_only=True)
    meldingsnummer_lijst = serializers.SerializerMethodField()

    def get_meldingsnummer_lijst(self, obj):
        return [
            signaal.signaal_data.get("meta", {}).get("meldingsnummerField")
            for signaal in obj.signalen_voor_melding.all()
        ]

    class Meta:
        model = Melding
        fields = (
            "_links",
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
            "meldinggebeurtenissen",
            "taakopdrachten_voor_melding",
            "signalen_voor_melding",
            "meldingsnummer_lijst",
        )
