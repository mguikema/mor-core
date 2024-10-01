from apps.meldingen.models import Melding
from apps.taken.filtersets import TaakopdrachtFilter
from apps.taken.models import Taakgebeurtenis, Taakopdracht
from apps.taken.serializers import (
    TaakgebeurtenisSerializer,
    TaakgebeurtenisStatusSerializer,
    TaakopdrachtSerializer,
    TaakopdrachtVerwijderenSerializer,
    TaaktypeAantallenSerializer,
)
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class TaakgebeurtenisViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Taakgebeurtenis viewset
    """

    lookup_field = "uuid"
    queryset = Taakgebeurtenis.objects.all()

    serializer_class = TaakgebeurtenisSerializer


class TaakopdrachtViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Taakopdracht
    """

    lookup_field = "uuid"
    queryset = Taakopdracht.objects.all()

    serializer_class = TaakopdrachtSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = TaakopdrachtFilter

    @extend_schema(
        description="Verander de status van een taak",
        request=TaakgebeurtenisStatusSerializer,
        responses={status.HTTP_200_OK: TaakopdrachtSerializer},
        parameters=None,
    )
    @action(detail=True, methods=["patch"], url_path="status-aanpassen")
    def status_aanpassen(self, request, uuid):
        taakopdracht = self.get_object()
        data = {}
        data.update(request.data)
        data["taakstatus"]["taakopdracht"] = taakopdracht.id
        serializer = TaakgebeurtenisStatusSerializer(
            data=data,
            context={"request": request},
        )
        if serializer.is_valid():
            externr_niet_opgelost = request.data.get("externr_niet_opgelost", False)
            Melding.acties.taakopdracht_status_aanpassen(
                serializer,
                taakopdracht,
                request=request,
                externr_niet_opgelost=externr_niet_opgelost,
            )

            serializer = TaakopdrachtSerializer(
                self.get_object(), context={"request": request}
            )
            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    def destroy(self, request, *args, **kwargs):
        taakopdracht = self.get_object()

        if taakopdracht.verwijderd_op:
            raise serializers.ValidationError("Deze taakopdracht is al verwijderd")

        taakgebeurtenis = Melding.acties.taakopdracht_verwijderen(
            taakopdracht, gebruiker=request.GET.get("gebruiker")
        )

        serializer = TaakopdrachtVerwijderenSerializer(
            taakgebeurtenis, context={"request": request}
        )
        return Response(serializer.data)

    @extend_schema(
        description="Taaktype aantallen per melding",
        responses={status.HTTP_200_OK: TaaktypeAantallenSerializer()},
        parameters=[
            OpenApiParameter(
                "melding_afgesloten_op_gte",
                OpenApiTypes.DATETIME,
                OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                "melding_afgesloten_op_lt",
                OpenApiTypes.DATETIME,
                OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                "inclusief-melding",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
            ),
        ],
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="taaktype-aantallen-per-melding",
        serializer_class=TaaktypeAantallenSerializer,
    )
    def taaktype_aantallen_per_melding(self, request):
        serializer = TaaktypeAantallenSerializer(
            self.filter_queryset(self.get_queryset()).taaktype_aantallen_per_melding(
                request.GET
            ),
            context={"request": request},
            many=True,
        )
        return Response(serializer.data)

    @extend_schema(
        description="Taakopdracht doorlooptijden en aantallen voor afgeronde taken per taaktype. Uniek o.b.v. onderwerp, wijk en taaktype ",
        responses={status.HTTP_200_OK: TaaktypeAantallenSerializer()},
        parameters=[
            OpenApiParameter(
                "afgesloten_op_gte",
                OpenApiTypes.DATETIME,
                OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                "afgesloten_op_lt",
                OpenApiTypes.DATETIME,
                OpenApiParameter.QUERY,
            ),
        ],
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="taakopdracht-doorlooptijden",
        serializer_class=TaaktypeAantallenSerializer,
    )
    def taakopdracht_doorlooptijden(self, request):
        serializer = TaaktypeAantallenSerializer(
            self.filter_queryset(self.get_queryset()).taakopdracht_doorlooptijden(),
            context={"request": request},
            many=True,
        )
        return Response(serializer.data)

    @extend_schema(
        description="Niewe taakopdracht. Uniek o.b.v. onderwerp, wijk en taaktype ",
        responses={status.HTTP_200_OK: TaaktypeAantallenSerializer()},
        parameters=[
            OpenApiParameter(
                "aangemaakt_op_gte",
                OpenApiTypes.DATETIME,
                OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                "aangemaakt_op_lt",
                OpenApiTypes.DATETIME,
                OpenApiParameter.QUERY,
            ),
        ],
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="nieuwe-taakopdrachten",
        serializer_class=TaaktypeAantallenSerializer,
    )
    def nieuwe_taakopdrachten(self, request):
        serializer = TaaktypeAantallenSerializer(
            self.filter_queryset(self.get_queryset()).nieuwe_taakopdrachten(),
            context={"request": request},
            many=True,
        )
        return Response(serializer.data)
