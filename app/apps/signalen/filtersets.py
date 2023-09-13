from apps.signalen.models import Signaal
from django_filters import rest_framework as filters


class SignaalFilter(filters.FilterSet):
    signaal_url = filters.CharFilter(field_name="signaal_url")

    class Meta:
        model = Signaal
        fields = [
            "signaal_url",
        ]
