from apps.meldingen.models import Bijlage
from apps.taken.serializers import BijlageSerializer
from rest_framework import mixins, viewsets


class BijlageViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    Bijlage viewset
    """

    queryset = Bijlage.objects.all()

    serializer_class = BijlageSerializer
