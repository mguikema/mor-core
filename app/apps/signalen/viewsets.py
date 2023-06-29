from apps.signalen.models import Signaal
from apps.signalen.serializers import SignaalSerializer
from rest_framework import mixins, viewsets


class SignaalViewSet(
    mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    lookup_field = "uuid"

    queryset = Signaal.objects.all()

    serializer_class = SignaalSerializer
