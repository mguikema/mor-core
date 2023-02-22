from apps.mor.models import TaakApplicatie
from rest_framework import serializers


class TaakApplicatieSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaakApplicatie
        fields = "__all__"
