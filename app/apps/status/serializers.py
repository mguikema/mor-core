from apps.status.models import Status
from rest_framework import serializers


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = (
            "naam",
            "melding",
        )

    def validate(self, attrs):
        melding = attrs.get("melding")
        nieuwe_status_naam = attrs.get("naam")
        if (
            nieuwe_status_naam
            and melding.status
            and not melding.status.status_verandering_toegestaan(nieuwe_status_naam)
        ):
            raise Status.StatusVeranderingNietToegestaan(
                f"Vorige status: {melding.status.naam} -> Nieuwe status: {nieuwe_status_naam}"
            )
        return attrs
