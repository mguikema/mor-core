from apps.meldingen.models import Melding
from apps.signalen.filtersets import SignaalFilter
from apps.signalen.models import Signaal
from apps.signalen.serializers import SignaalSerializer
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response


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
    # permission_classes = ()
    queryset = Signaal.objects.all()

    serializer_class = SignaalSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = SignaalFilter

    def create(self, request):
        print("create")
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        print("create")
        if serializer.is_valid():
            print(serializer.validated_data)
            Melding.acties.signaal_aanmaken(serializer)
            return Response(serializer.validated_data)
        print(serializer.errors)
        return Response(
            data=serializer.errors,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
