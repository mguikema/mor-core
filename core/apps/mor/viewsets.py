from apps.mor.models import TaakApplicatie
from apps.mor.serializers import TaakApplicatieSerializer
from rest_framework import viewsets


class TaakApplicatieViewSet(viewsets.ModelViewSet):

    queryset = TaakApplicatie.objects.all()

    serializer_class = TaakApplicatieSerializer
