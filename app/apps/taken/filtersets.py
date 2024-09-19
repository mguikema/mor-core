from apps.taken.models import Taakopdracht
from django_filters import rest_framework as filters


class TaakopdrachtFilter(filters.FilterSet):
    melding_afgesloten_op_gte = filters.DateTimeFilter(
        field_name="melding__afgesloten_op", lookup_expr="gte"
    )
    melding_afgesloten_op_gt = filters.DateTimeFilter(
        field_name="melding__afgesloten_op", lookup_expr="gt"
    )
    melding_afgesloten_op_lte = filters.DateTimeFilter(
        field_name="melding__afgesloten_op", lookup_expr="lte"
    )
    melding_afgesloten_op_lt = filters.DateTimeFilter(
        field_name="melding__afgesloten_op", lookup_expr="lt"
    )

    class Meta:
        model = Taakopdracht
        fields = [
            "melding",
        ]
