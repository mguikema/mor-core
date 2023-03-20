from apps.classificatie.models import Onderwerp
from rest_framework import serializers


class OnderwerpSerializer(serializers.ModelSerializer):
    """
    Onderwerp van een Melding of Signaal
    """

    class Meta:
        model = Onderwerp
        fields = (
            "naam",
            "id",
            "slug",
        )
        read_only_fields = (
            "id",
            "slug",
        )
