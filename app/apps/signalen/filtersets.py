from typing import List, Tuple

from apps.signalen.models import Signaal
from django.db import models
from django_filters import rest_framework as filters
from rest_framework import filters as rest_filters


class SignaalFilter(filters.FilterSet):
    signaal_url = filters.CharFilter(field_name="signaal_url")
    origineel_aangemaakt_gte = filters.DateTimeFilter(
        field_name="origineel_aangemaakt", lookup_expr="gte"
    )
    origineel_aangemaakt_gt = filters.DateTimeFilter(
        field_name="origineel_aangemaakt", lookup_expr="gt"
    )
    origineel_aangemaakt_lte = filters.DateTimeFilter(
        field_name="origineel_aangemaakt", lookup_expr="lte"
    )
    origineel_aangemaakt_lt = filters.DateTimeFilter(
        field_name="origineel_aangemaakt", lookup_expr="lt"
    )
    melding__origineel_aangemaakt_gte = filters.DateTimeFilter(
        field_name="melding__origineel_aangemaakt", lookup_expr="gte"
    )

    class Meta:
        model = Signaal
        fields = [
            "signaal_url",
            "melding",
        ]


class RelatedOrderingFilter(rest_filters.OrderingFilter):
    _max_related_depth = 3

    @staticmethod
    def _get_verbose_name(field: models.Field, non_verbose_name: str) -> str:
        return (
            field.verbose_name
            if hasattr(field, "verbose_name")
            else non_verbose_name.replace("_", " ")
        )

    def _retrieve_all_related_fields(
        self, fields: Tuple[models.Field], model: models.Model, depth: int = 0
    ) -> List[tuple]:
        valid_fields = []
        if depth > self._max_related_depth:
            return valid_fields
        for field in fields:
            if field.related_model and field.related_model != model:
                rel_fields = self._retrieve_all_related_fields(
                    field.related_model._meta.get_fields(),
                    field.related_model,
                    depth + 1,
                )
                for rel_field in rel_fields:
                    valid_fields.append(
                        (
                            f"{field.name}__{rel_field[0]}",
                            self._get_verbose_name(field, rel_field[1]),
                        )
                    )
            else:
                valid_fields.append(
                    (
                        field.name,
                        self._get_verbose_name(field, field.name),
                    )
                )
        return valid_fields

    def get_valid_fields(
        self, queryset: models.QuerySet, view, context: dict = None
    ) -> List[tuple]:
        valid_fields = getattr(view, "ordering_fields", self.ordering_fields)
        if valid_fields != "__all_related__":
            if not context:
                context = {}
            valid_fields = super().get_valid_fields(queryset, view, context)
        else:
            valid_fields = [
                *self._retrieve_all_related_fields(
                    queryset.model._meta.get_fields(),
                    queryset.model,
                ),
                *[(key, key.title().split("__")) for key in queryset.query.annotations],
            ]
        return valid_fields
