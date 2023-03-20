from apps.classificatie.models import Onderwerp
from apps.classificatie.serializers import OnderwerpSerializer
from rest_framework import mixins, viewsets


class OnderwerpViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Onderwerpen voor Meldingen en Signalen
    """

    queryset = Onderwerp.objects.all()

    serializer_class = OnderwerpSerializer
