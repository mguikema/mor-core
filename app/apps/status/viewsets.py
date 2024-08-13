import logging

from apps.status.filtersets import StatusFilter
from apps.status.models import Status
from apps.status.serializers import StatusSerializer, StatusVeranderingSerializer
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class StatusViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    queryset = Status.objects.all()

    serializer_class = StatusSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = StatusFilter

    @extend_schema(
        description="Unieke status verandering duur per wijk en onderwerp",
        responses={status.HTTP_200_OK: StatusVeranderingSerializer(many=True)},
        parameters=None,
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="veranderingen",
        serializer_class=StatusVeranderingSerializer,
        permission_classes=(),
    )
    def veranderingen(self, request):
        serializer = StatusVeranderingSerializer(
            self.filter_queryset(self.get_queryset()).get_veranderingen(request.GET),
            context={"request": request},
            many=True,
        )
        return Response(serializer.data)
