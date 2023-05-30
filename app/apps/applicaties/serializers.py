from apps.aliassen.serializers import OnderwerpAliasSerializer
from apps.applicaties.models import Taakapplicatie
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.reverse import reverse


class TaakapplicatieLinksSerializer(serializers.Serializer):
    self = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.URI)
    def get_self(self, obj):
        return reverse(
            "v1:taakapplicatie-detail",
            kwargs={"uuid": obj.uuid},
            request=self.context.get("request"),
        )


class TaakapplicatieSerializer(serializers.ModelSerializer):
    _links = TaakapplicatieLinksSerializer(source="*")
    onderwerpen = OnderwerpAliasSerializer(many=True)

    class Meta:
        model = Taakapplicatie
        fields = (
            "_links",
            "uuid",
            "naam",
            "basis_url",
            "onderwerpen",
            "taaktypes",
        )
        read_only_fields = (
            "_links",
            "uuid",
            "naam",
            "basis_url",
            "onderwerpen",
            "taaktypes",
        )
