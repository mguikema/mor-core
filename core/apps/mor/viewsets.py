from apps.mor.filtersets import MeldingFilter, RelatedOrderingFilter
from apps.mor.models import (
    Bijlage,
    Melder,
    Melding,
    MeldingGebeurtenis,
    MeldingGebeurtenisType,
    Signaal,
    TaakApplicatie,
)
from apps.mor.serializers import (
    BijlageSerializer,
    GeometrieSerializer,
    MelderSerializer,
    MeldingDetailSerializer,
    MeldingGebeurtenisSerializer,
    MeldingGebeurtenisTypeSerializer,
    MeldingSerializer,
    SignaalSerializer,
    TaakApplicatieSerializer,
)
from django_filters import rest_framework as filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, viewsets


class BijlageViewSet(viewsets.ModelViewSet):
    """
    Bijlage comment van viewset
    """

    queryset = Bijlage.objects.all()

    serializer_class = BijlageSerializer


class TaakApplicatieViewSet(viewsets.ModelViewSet):

    queryset = TaakApplicatie.objects.all()

    serializer_class = TaakApplicatieSerializer


class MeldingGebeurtenisTypeViewSet(viewsets.ModelViewSet):

    queryset = MeldingGebeurtenisType.objects.all()

    serializer_class = MeldingGebeurtenisTypeSerializer


class MeldingGebeurtenisViewSet(viewsets.ModelViewSet):

    queryset = MeldingGebeurtenis.objects.all()

    serializer_class = MeldingGebeurtenisSerializer


class MelderViewSet(viewsets.ModelViewSet):

    queryset = Melder.objects.all()

    serializer_class = MelderSerializer


class SignaalViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):

    queryset = Signaal.objects.all()

    serializer_class = SignaalSerializer


@extend_schema(
    parameters=[
        OpenApiParameter("omschrijving", OpenApiTypes.STR, OpenApiParameter.QUERY),
        OpenApiParameter("onderwerp", OpenApiTypes.STR, OpenApiParameter.QUERY),
        OpenApiParameter("begraafplaats", OpenApiTypes.STR, OpenApiParameter.QUERY),
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

    queryset = Melding.objects.all()
    serializer_class = MeldingSerializer
    serializer_detail_class = MeldingDetailSerializer
    filter_backends = (
        filters.DjangoFilterBackend,
        RelatedOrderingFilter,
    )
    ordering_fields = "__all_related__"
    filterset_class = MeldingFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return self.serializer_detail_class
        return super().get_serializer_class()
