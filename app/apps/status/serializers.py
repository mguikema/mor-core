from apps.status.models import Status
from rest_framework import serializers


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = (
            "naam",
            "melding",
        )
        read_only_fields = ("melding",)
