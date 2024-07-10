import logging

from apps.meldingen.filtersets import (
    DjangoPreFilterBackend,
    MeldingFilter,
    MeldingPreFilter,
    RelatedOrderingFilter,
)
from apps.meldingen.models import Melding, Meldinggebeurtenis
from apps.meldingen.serializers import (
    MeldingAantallenSerializer,
    MeldingDetailSerializer,
    MeldinggebeurtenisSerializer,
    MeldingGebeurtenisStatusSerializer,
    MeldingGebeurtenisUrgentieSerializer,
    MeldingSerializer,
)
from apps.taken.serializers import TaakopdrachtSerializer
from config.context import db
from django.conf import settings
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class MeldinggebeurtenisViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    lookup_field = "uuid"
    queryset = Meldinggebeurtenis.objects.all()

    serializer_class = MeldinggebeurtenisSerializer


@extend_schema(
    parameters=[
        OpenApiParameter("omschrijving", OpenApiTypes.STR, OpenApiParameter.QUERY),
        OpenApiParameter("onderwerp", OpenApiTypes.INT, OpenApiParameter.QUERY),
        OpenApiParameter("status", OpenApiTypes.STR, OpenApiParameter.QUERY),
        OpenApiParameter("begraafplaats", OpenApiTypes.INT, OpenApiParameter.QUERY),
        OpenApiParameter("begraafplaats_vak", OpenApiTypes.STR, OpenApiParameter.QUERY),
        OpenApiParameter(
            "begraafplaats_grafnummer", OpenApiTypes.STR, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "begraafplaats_grafnummer_gte", OpenApiTypes.INT, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "begraafplaats_grafnummer_gt", OpenApiTypes.INT, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "begraafplaats_grafnummer_lte", OpenApiTypes.INT, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "begraafplaats_grafnummer_lt", OpenApiTypes.INT, OpenApiParameter.QUERY
        ),
        OpenApiParameter("meta__categorie", OpenApiTypes.STR, OpenApiParameter.QUERY),
        OpenApiParameter(
            "aangemaakt_op_gte", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "aangemaakt_op_gt", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "aangemaakt_op_lte", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "aangemaakt_op_lt", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "aangepast_op_gte", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "aangepast_op_gt", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "aangepast_op_lte", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "aangepast_op_lt", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "origineel_aangemaakt_gte", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "origineel_aangemaakt_gt", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "origineel_aangemaakt_lte", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "origineel_aangemaakt_lt", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "afgesloten_op_gte", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "afgesloten_op_gt", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "afgesloten_op_lte", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "afgesloten_op_lt", OpenApiTypes.DATETIME, OpenApiParameter.QUERY
        ),
        OpenApiParameter(
            "actieve_meldingen", OpenApiTypes.BOOL, OpenApiParameter.QUERY
        ),
    ]
)
class MeldingViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "uuid"
    queryset = (
        Melding.objects.select_related(
            "status",
        )
        .prefetch_related(
            "locaties_voor_melding",
            "signalen_voor_melding__bijlagen",
            "bijlagen",
            "onderwerpen",
            "meldinggebeurtenissen_voor_melding__bijlagen",
            "taakopdrachten_voor_melding__status",
            "taakopdrachten_voor_melding__taakgebeurtenissen_voor_taakopdracht__bijlagen",
        )
        .all()
    )
    prefiltered_queryset = None
    serializer_class = MeldingSerializer
    serializer_detail_class = MeldingDetailSerializer
    pre_filter_backends = (DjangoPreFilterBackend,)
    filter_backends = (
        filters.DjangoFilterBackend,
        RelatedOrderingFilter,
    )
    ordering_fields = "__all_related__"
    filterset_class = MeldingFilter
    pre_filterset_class = MeldingPreFilter
    filter_options_fields = (
        (
            "begraafplaats",
            "locaties_voor_melding__begraafplaats",
            "meta_uitgebreid__begraafplaats__choices",
            "signalen_voor_melding__meta_uitgebreid__begraafplaats__choices",
        ),
        (
            "buurt",
            "locaties_voor_melding__buurtnaam",
            None,
            None,
            "locaties_voor_melding__wijknaam",
        ),
        (
            "onderwerp",
            "onderwerpen",
            "onderwerpen__bron_url",
        ),
    )

    def get_queryset(self):
        if self.action == "retrieve":
            return (
                Melding.objects.select_related(
                    "status",
                )
                .prefetch_related(
                    "bijlagen",
                    "signalen_voor_melding__bijlagen",
                    "meldinggebeurtenissen_voor_melding__bijlagen",
                    "meldinggebeurtenissen_voor_melding__status",
                    "meldinggebeurtenissen_voor_melding__locatie",
                    "meldinggebeurtenissen_voor_melding__taakgebeurtenis__taakopdracht",
                    "meldinggebeurtenissen_voor_melding__taakgebeurtenis__bijlagen",
                    "meldinggebeurtenissen_voor_melding__taakgebeurtenis__taakstatus",
                    "taakopdrachten_voor_melding__applicatie",
                    "taakopdrachten_voor_melding__status",
                    "taakopdrachten_voor_melding__taakgebeurtenissen_voor_taakopdracht__bijlagen",
                    "taakopdrachten_voor_melding__taakgebeurtenissen_voor_taakopdracht__taakstatus",
                    "locaties_voor_melding",
                )
                .all()
            )
        return super().get_queryset()

    def get_prefiltered_queryset(self):
        assert self.prefiltered_queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method." % self.__class__.__name__
        )

        queryset = self.prefiltered_queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def filter_queryset(self, queryset):
        for backend in list(self.pre_filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        self.prefiltered_queryset = queryset
        return super().filter_queryset(queryset)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return self.serializer_detail_class
        return super().get_serializer_class()

    def list(self, request):
        with db(settings.READONLY_DATABASE_KEY):
            return super().list(request)

    def retrieve(self, request, uuid=None):
        with db(settings.READONLY_DATABASE_KEY):
            return super().retrieve(request, uuid)

    @extend_schema(
        description="Verander de status van een melding",
        request=MeldingGebeurtenisStatusSerializer,
        responses={status.HTTP_200_OK: MeldingDetailSerializer},
        parameters=None,
    )
    @action(detail=True, methods=["patch"], url_path="status-aanpassen")
    def status_aanpassen(self, request, uuid):
        melding = self.get_object()
        data = {"melding": melding.id}
        data.update(request.data)
        data["status"]["melding"] = melding.id
        data["gebeurtenis_type"] = Meldinggebeurtenis.GebeurtenisType.STATUS_WIJZIGING
        serializer = MeldingGebeurtenisStatusSerializer(
            data=data,
            context={"request": request},
        )
        if serializer.is_valid():
            Melding.acties.status_aanpassen(serializer, self.get_object())

            serializer = MeldingDetailSerializer(
                self.get_object(), context={"request": request}
            )

            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @extend_schema(
        description="Melding heropenen",
        request=MeldingGebeurtenisStatusSerializer,
        responses={status.HTTP_200_OK: MeldingDetailSerializer},
        parameters=None,
    )
    @action(detail=True, methods=["patch"], url_path="heropenen")
    def heropenen(self, request, uuid):
        melding = self.get_object()
        data = {"melding": melding.id}
        data.update(request.data)
        data["status"]["melding"] = melding.id
        data["gebeurtenis_type"] = Meldinggebeurtenis.GebeurtenisType.MELDING_HEROPEND
        serializer = MeldingGebeurtenisStatusSerializer(
            data=data,
            context={"request": request},
        )
        if serializer.is_valid():
            Melding.acties.status_aanpassen(serializer, self.get_object(), heropen=True)

            serializer = MeldingDetailSerializer(
                self.get_object(), context={"request": request}
            )
            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @extend_schema(
        description="Verander de urgentie van een melding",
        request=MeldingGebeurtenisUrgentieSerializer,
        responses={status.HTTP_200_OK: MeldingDetailSerializer},
        parameters=None,
    )
    @action(detail=True, methods=["patch"], url_path="urgentie-aanpassen")
    def urgentie_aanpassen(self, request, uuid):
        melding = self.get_object()
        data = {"melding": melding.id}
        data.update(request.data)
        data["gebeurtenis_type"] = Meldinggebeurtenis.GebeurtenisType.URGENTIE_AANGEPAST
        serializer = MeldingGebeurtenisUrgentieSerializer(
            data=data,
            context={"request": request},
        )
        if serializer.is_valid():
            Melding.acties.urgentie_aanpassen(serializer, self.get_object())

            serializer = MeldingDetailSerializer(
                self.get_object(), context={"request": request}
            )
            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @extend_schema(
        description="Gebeurtenis voor een melding toevoegen",
        request=MeldinggebeurtenisSerializer,
        responses={status.HTTP_200_OK: MeldingDetailSerializer},
        parameters=None,
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="gebeurtenis-toevoegen",
        serializer_class=MeldinggebeurtenisSerializer,
    )
    def gebeurtenis_toevoegen(self, request, uuid):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            Melding.acties.gebeurtenis_toevoegen(serializer, self.get_object())

            serializer = MeldingDetailSerializer(
                self.get_object(), context={"request": request}
            )
            return Response(serializer.data)
        return Response(
            data=serializer.errors,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @extend_schema(
        description="Taakopdracht voor een melding toevoegen",
        request=TaakopdrachtSerializer,
        responses={status.HTTP_200_OK: TaakopdrachtSerializer},
        parameters=None,
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="taakopdracht",
        serializer_class=TaakopdrachtSerializer,
    )
    def taakopdracht_aanmaken(self, request, uuid):
        melding = self.get_object()
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            taakopdracht = Melding.acties.taakopdracht_aanmaken(
                serializer, melding, request
            )

            serializer = TaakopdrachtSerializer(
                taakopdracht, context={"request": request}
            )
            return Response(serializer.data)

        return Response(
            data=serializer.errors,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @extend_schema(
        description="Locatie aanmaken voor een melding",
        request=MeldinggebeurtenisSerializer,
        responses={status.HTTP_200_OK: MeldingDetailSerializer},
        parameters=None,
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="locatie-aanmaken",
        serializer_class=MeldinggebeurtenisSerializer,
    )
    def locatie_aanmaken(self, request, uuid):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        try:
            serializer.is_valid(raise_exception=True)
            Melding.acties.gebeurtenis_toevoegen(serializer, self.get_object())

            serializer_data = MeldingDetailSerializer(
                self.get_object(), context={"request": request}
            ).data

            # Use JsonResponse for both success and error cases
            return Response(serializer_data, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            logger.error(e)
            # Return a JsonResponse with the error details
            return JsonResponse(
                {"error": "Invalid data", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            # Return a JsonResponse with the specific error message
            logger.error(e)
            return JsonResponse(
                {"error": "An internal server error occurred!"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        description="Melding aantallen per wijk en onderwerp",
        responses={status.HTTP_200_OK: MeldingAantallenSerializer(many=True)},
        parameters=None,
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="aantallen",
        serializer_class=MeldingAantallenSerializer,
    )
    def aantallen(self, request):
        serializer = MeldingAantallenSerializer(
            self.filter_queryset(self.get_queryset()).get_aantallen(),
            context={"request": request},
            many=True,
        )
        return Response(serializer.data)
