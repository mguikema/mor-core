from apps.status.models import Status
from django_filters import rest_framework as filters


class StatusFilter(filters.FilterSet):
    aangemaakt_op_gte = filters.DateTimeFilter(
        field_name="aangemaakt_op", lookup_expr="gte"
    )
    aangemaakt_op_gt = filters.DateTimeFilter(
        field_name="aangemaakt_op", lookup_expr="gt"
    )
    aangemaakt_op_lte = filters.DateTimeFilter(
        field_name="aangemaakt_op", lookup_expr="lte"
    )
    aangemaakt_op_lt = filters.DateTimeFilter(
        field_name="aangemaakt_op", lookup_expr="lt"
    )

    class Meta:
        model = Status
        fields = [
            "aangemaakt_op",
        ]
