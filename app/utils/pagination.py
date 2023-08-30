from collections import OrderedDict

from django.db.models import Count
from rest_framework.pagination import LimitOffsetPagination as DRFLimitOffsetPagination
from rest_framework.response import Response


class LimitOffsetPagination(DRFLimitOffsetPagination):
    """
    Als je de attribute 'filter_options_fields' zoals het voorbeeld hieronder, zet op de viewset

    filter_options_fields = (
        "status__naam",
    )

    In de paginated response zal de key 'filter_options', worden toegevoegd, met als waarde zoals het voorbeeld hieronder.
    {
        "status__naam":{
            "gemeld":[
                "gemeld",
                1038
            ],
            "in_behandeling":[
                "in_behandeling",
                3
            ]
    },

    Complexere lookups kunnen als hieronder worden samen gesteld

    filter_options_fields = (
        ("status", "status__id", "status__naam", ),
    )
    Het eerste item wordt de key in de dict 'filter_options'
    Het tweede item wordt gebruikt voor de distinct en count in de queryset
    Met het derde item wordt de value(leesbare waarde) opgezocht in het record, ook kan je hier in een dict uit een json field de waarde halen.

    """

    def paginate_queryset(
        self, filtered_queryset, request, view=None
    ):  # pragma: no cover
        self.filter_options = {}
        if view and hasattr(view, "filter_options_fields"):
            self.filter_options = self._get_filter_options(
                filtered_queryset, view.get_queryset(), view.filter_options_fields
            )
        return super().paginate_queryset(filtered_queryset, request, view)

    def get_paginated_response(self, data):
        default_repsonse_data = [
            ("count", self.count),
            ("next", self.get_next_link()),
            ("previous", self.get_previous_link()),
            ("results", data),
        ]
        if self.filter_options:
            default_repsonse_data.insert(3, ("filter_options", self.filter_options))
        return Response(OrderedDict(default_repsonse_data))

    def _get_filter_options(self, f_qs, qs, fields=[]):
        out = {}

        def value_lookup(obj, key, f: list | tuple):
            if isinstance(obj, dict):
                return obj.get(key, key)
            if isinstance(obj, (str, int)):
                return obj
            return key

        for f in fields:
            f = f if isinstance(f, (list, tuple)) else (f,)
            key = f[1] if len(f) > 1 else f[0]
            value_lookup_str = f[2] if len(f) > 2 else key
            f_dict = {
                ll[0]: (value_lookup(ll[1], ll[0], f), 0)
                for ll in qs.order_by(key)
                .values_list(key, value_lookup_str)
                .distinct(key)
            }
            ff_dict = {
                fl[0]: (value_lookup(fl[1], fl[0], f), fl[2])
                for fl in f_qs.order_by(key)
                .values_list(key, value_lookup_str)
                .annotate(count=Count(key))
            }
            f_dict.update(ff_dict)
            f_dict = {k: v for k, v in f_dict.items() if k}
            out[f[0]] = f_dict
        return out
