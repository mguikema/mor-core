from apps.signalen.filtersets import SignaalFilter
from apps.signalen.models import Signaal
from apps.signalen.serializers import SignaalSerializer
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, viewsets


@extend_schema(
    parameters=[
        OpenApiParameter("signaal_url", OpenApiTypes.URI, OpenApiParameter.QUERY),
    ]
)
class SignaalViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"

    queryset = Signaal.objects.all()

    serializer_class = SignaalSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = SignaalFilter
