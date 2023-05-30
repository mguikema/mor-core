from apps.applicaties.models import Taakapplicatie
from apps.applicaties.serializers import TaakapplicatieSerializer
from rest_framework import viewsets


class TaakapplicatieViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Taakapplicaties voor MOR
    """

    queryset = Taakapplicatie.objects.all()

    permission_classes = ()

    serializer_class = TaakapplicatieSerializer
    lookup_field = "uuid"
