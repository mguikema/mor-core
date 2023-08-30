from apps.classificatie.models import Onderwerp
from django.urls import reverse
from rest_framework import serializers


class OnderwerpSerializer(serializers.ModelSerializer):

    """
    Onderwerp van een Melding of Signaal
    """

    absolute_uri = serializers.SerializerMethodField()

    class Meta:
        model = Onderwerp
        fields = (
            "name",
            "id",
            "slug",
            "absolute_uri",
        )
        read_only_fields = (
            "id",
            "slug",
            "absolute_uri",
        )
        lookup_field = "slug"

    def get_absolute_uri(self, obj):
        url = reverse("app:onderwerp-detail", kwargs={"slug": obj.slug})
        request = self.context.get("request")
        return request.build_absolute_uri(url)
