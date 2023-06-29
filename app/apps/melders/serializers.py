from apps.melders.models import Melder
from drf_writable_nested.serializers import WritableNestedModelSerializer


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
