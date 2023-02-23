from apps.mor.models import (
    Bijlage,
    Geometrie,
    Melding,
    MeldingGebeurtenis,
    MeldingGebeurtenisType,
    Signaal,
    TaakApplicatie,
)
from apps.mor.serializers import (
    BijlageSerializer,
    GeometrieSerializer,
    MeldingGebeurtenisSerializer,
    MeldingGebeurtenisTypeSerializer,
    MeldingSerializer,
    SignaalSerializer,
    TaakApplicatieSerializer,
)
from rest_framework import viewsets


class BijlageViewSet(viewsets.ModelViewSet):

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


class SignaalViewSet(viewsets.ModelViewSet):

    queryset = Signaal.objects.all()

    serializer_class = SignaalSerializer


class MeldingViewSet(viewsets.ModelViewSet):

    queryset = Melding.objects.all()

    serializer_class = MeldingSerializer
