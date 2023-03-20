from apps.mor.models import (
    Bijlage,
    Geometrie,
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
    MeldingGebeurtenisSerializer,
    MeldingGebeurtenisTypeSerializer,
    MeldingSerializer,
    SignaalSerializer,
    TaakApplicatieSerializer,
)
from rest_framework import viewsets


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


class GeometrieViewSet(viewsets.ModelViewSet):

    queryset = Geometrie.objects.all()

    serializer_class = GeometrieSerializer


class MelderViewSet(viewsets.ModelViewSet):

    queryset = Melder.objects.all()

    serializer_class = MelderSerializer


class SignaalViewSet(viewsets.ModelViewSet):

    queryset = Signaal.objects.all()

    serializer_class = SignaalSerializer


class MeldingViewSet(viewsets.ModelViewSet):

    queryset = Melding.objects.all()

    serializer_class = MeldingSerializer
