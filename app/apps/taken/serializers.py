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
from apps.taken.models import Taakopdracht, Taakstatus
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.reverse import reverse


class TaakopdrachtLinksSerializer(serializers.Serializer):
    taakapplicatie = serializers.SerializerMethodField()
    melding = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.URI)
    def get_taakapplicatie(self, obj):
        return reverse(
            "v1:taakapplicatie-detail",
            kwargs={"uuid": obj.taakapplicatie.uuid},
            request=self.context.get("request"),
        )

    @extend_schema_field(OpenApiTypes.URI)
    def get_melding(self, obj):
        return reverse(
            "v1:melding-detail",
            kwargs={"uuid": obj.melding.uuid},
            request=self.context.get("request"),
        )


class TaakstatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taakstatus
        fields = ("naam",)
        read_only_fields = ("naam",)


class TaakopdrachtSerializer(serializers.ModelSerializer):
    _links = TaakopdrachtLinksSerializer(source="*", read_only=True)
    taaktype = serializers.URLField()
    status = TaakstatusSerializer()

    class Meta:
        model = Taakopdracht
        fields = (
            "_links",
            "uuid",
            "taaktype",
            "titel",
            "bericht",
            "additionele_informatie",
            "status",
            "melding",
        )
        read_only_fields = (
            "_links",
            "uuid",
            "status",
            "melding",
        )
