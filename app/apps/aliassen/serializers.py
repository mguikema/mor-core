from apps.aliassen.models import OnderwerpAlias
from rest_framework import serializers


class OnderwerpAliasSerializer(serializers.ModelSerializer):

    """
    OnderwerpAlias van een Melding of Signaal
    """

    class Meta:
        model = OnderwerpAlias
        fields = (
            "bron_url",
            "response_json",
        )
        read_only_fields = (
            "bron_url",
            "response_json",
        )
