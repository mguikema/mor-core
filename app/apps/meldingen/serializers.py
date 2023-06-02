from apps.aliassen.serializers import OnderwerpAliasSerializer
from apps.bijlagen.serializers import BijlageSerializer
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
    taakgebeurtenis = TaakgebeurtenisSerializer()

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
            "taakgebeurtenis",
        )
        read_only_fields = (
            "aangemaakt_op",
            "gebeurtenis_type",
            "status",
            "taakgebeurtenis",
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
    _links = MeldingLinksSerializer(source="*")
    locaties_voor_melding = LocatieRelatedField(many=True, read_only=True)
    bijlagen = BijlageRelatedField(many=True, read_only=True)
    status = StatusSerializer()
    volgende_statussen = serializers.ListField(
        source="status.volgende_statussen",
        child=serializers.CharField(),
        read_only=True,
    )
    aantal_actieve_taken = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.INT)
    def get_aantal_actieve_taken(self, obj):
        return obj.actieve_taakopdrachten().count()

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
        )


class MeldingDetailSerializer(MeldingSerializer):
    _links = MeldingLinksSerializer(source="*")
    locaties_voor_melding = LocatieRelatedField(many=True, read_only=True)
    onderwerpen = OnderwerpAliasSerializer(many=True, read_only=True)
    bijlagen = BijlageRelatedField(many=True, read_only=True)
    status = StatusSerializer()
    volgende_statussen = serializers.ListField(
        source="status.volgende_statussen",
        child=serializers.CharField(),
        read_only=True,
    )
    meldinggebeurtenissen = MeldingGebeurtenisSerializer(
        source="meldinggebeurtenissen_voor_melding", many=True, read_only=True
    )
    taakopdrachten_voor_melding = TaakopdrachtSerializer(
        source="actieve_taakopdrachten", many=True, read_only=True
    )

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
        )
