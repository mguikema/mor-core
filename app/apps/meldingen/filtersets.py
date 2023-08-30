import operator
from functools import reduce
from typing import List, Tuple

from apps.meldingen.models import Melding
from django.contrib.postgres.search import TrigramSimilarity
from django.db import models
from django.db.models import Q
from django.db.models.functions import Greatest
from django.forms.fields import CharField, MultipleChoiceField
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from django_filters import utils
from rest_framework import filters as rest_filters
from rest_framework.filters import SearchFilter
from rest_framework.settings import api_settings


class DjangoFilterBackend(filters.DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filterset = self.get_filterset(request, queryset, view)
        # print(filterset.__class__)
        # print(filterset.Meta)
        print(filterset.Meta().default_prefix)
        # print(dir(filterset.Meta()))
        # print(filterset.__class__._meta)
        # print(dir(filterset.__class__._meta))
        # print(filterset.__class__._meta.default_prefix)
        if filterset is None:
            return queryset

        if not filterset.is_valid() and self.raise_exception:
            raise utils.translate_validation(filterset.errors)
        return filterset.qs


class MultipleValueField(MultipleChoiceField):
    def __init__(self, *args, field_class, **kwargs):
        self.inner_field = field_class()
        super().__init__(*args, **kwargs)

    def valid_value(self, value):
        return self.inner_field.validate(value)

    def clean(self, values):
        return values and [self.inner_field.clean(value) for value in values]


class MultipleValueFilter(filters.Filter):
    field_class = MultipleValueField

    def __init__(self, *args, field_class, **kwargs):
        kwargs.setdefault("lookup_expr", "in")
        super().__init__(*args, field_class=field_class, **kwargs)


class BasisFilter(filters.FilterSet):
    aangemaakt_op_gte = filters.DateTimeFilter(
        field_name="aangemaakt_op", lookup_expr="gte"
    )
    aangemaakt_op_gt = filters.DateTimeFilter(
        field_name="aangemaakt_op", lookup_expr="gt"
    )
    aangepast_op_gt = filters.DateTimeFilter(
        field_name="aangepast_op", lookup_expr="gt"
    )
    aangepast_op_gte = filters.DateTimeFilter(
        field_name="aangepast_op", lookup_expr="gte"
    )
    aangemaakt_op_lte = filters.DateTimeFilter(
        field_name="aangemaakt_op", lookup_expr="lte"
    )
    aangemaakt_op_lt = filters.DateTimeFilter(
        field_name="aangemaakt_op", lookup_expr="lt"
    )
    aangepast_op_lt = filters.DateTimeFilter(
        field_name="aangepast_op", lookup_expr="lt"
    )
    aangepast_op_lte = filters.DateTimeFilter(
        field_name="aangepast_op", lookup_expr="lte"
    )


class MeldingFilter(BasisFilter):
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

    afgesloten_op_gte = filters.DateTimeFilter(
        field_name="afgesloten_op", lookup_expr="gte"
    )
    afgesloten_op_gt = filters.DateTimeFilter(
        field_name="afgesloten_op", lookup_expr="gt"
    )
    afgesloten_op_lte = filters.DateTimeFilter(
        field_name="afgesloten_op", lookup_expr="lte"
    )
    afgesloten_op_lt = filters.DateTimeFilter(
        field_name="afgesloten_op", lookup_expr="lt"
    )

    omschrijving = filters.CharFilter(method="get_omschrijving")

    actieve_meldingen = filters.BooleanFilter(method="get_actieve_meldingen")
    onderwerp = MultipleValueFilter(field_class=CharField, method="get_onderwerpen")
    status = MultipleValueFilter(field_class=CharField, method="get_statussen")
    buurt = MultipleValueFilter(field_class=CharField, method="get_buurt")
    wijk = MultipleValueFilter(field_class=CharField, method="get_wijk")
    begraafplaats = MultipleValueFilter(
        field_class=CharField, method="get_begraafplaatsen"
    )
    begraafplaats_vak = filters.CharFilter(
        field_name="locaties_voor_melding__vak", lookup_expr="icontains"
    )
    begraafplaats_grafnummer = filters.CharFilter(
        field_name="locaties_voor_melding__grafnummer", lookup_expr="icontains"
    )
    begraafplaats_grafnummer_gte = filters.NumberFilter(
        method="get_begraafplaats_grafnummer"
    )
    begraafplaats_grafnummer_gt = filters.NumberFilter(
        method="get_begraafplaats_grafnummer"
    )
    begraafplaats_grafnummer_lte = filters.NumberFilter(
        method="get_begraafplaats_grafnummer"
    )
    begraafplaats_grafnummer_lt = filters.NumberFilter(
        method="get_begraafplaats_grafnummer"
    )

    # b&c
    meta__categorie = MultipleValueFilter(
        field_class=CharField, method="get_categories"
    )

    def get_begraafplaats_grafnummer(self, queryset, name, value):
        if value:
            valid_lookup_expr = ["gt", "gte", "lt", "lte"]
            lookup_expr = (
                name.rsplit("_", 1)[1] if name.rsplit("_", 1) else valid_lookup_expr[0]
            )
            lookup_expr = (
                lookup_expr
                if lookup_expr in valid_lookup_expr
                else valid_lookup_expr[0]
            )
            return queryset.filter(
                locaties_voor_melding__grafnummer__regex="^[0-9]+$"
            ).filter(Q(**{f"locaties_voor_melding__grafnummer__{lookup_expr}": value}))
        return queryset

    def get_omschrijving(self, queryset, name, value):
        if value:
            qs = (
                queryset.annotate(
                    similarity=TrigramSimilarity("omschrijving", str(value))
                )
                .filter(similarity__gt=0.3)
                .order_by("-similarity")
            )
            return qs
        return queryset

    def get_buurt(self, queryset, name, value):
        if value:
            return queryset.filter(
                locaties_voor_melding__buurtnaam__in=value
            ).distinct()
        return queryset

    def get_wijk(self, queryset, name, value):
        if value:
            return queryset.filter(locaties_voor_melding__wijknaam__in=value).distinct()
        return queryset

    def get_begraafplaatsen(self, queryset, name, value):
        if value:
            return queryset.filter(
                locaties_voor_melding__begraafplaats__in=value
            ).distinct()
        return queryset

    def get_statussen(self, queryset, name, value):
        if value:
            return queryset.filter(status__naam__in=value)
        return queryset

    def get_onderwerpen(self, queryset, name, value):
        if value:
            return queryset.filter(onderwerpen__in=value)
        return queryset

    def get_categories(self, queryset, name, value):
        if value:
            categories = (Q(meta__categorie__icontains=str(cat)) for cat in value)
            return queryset.filter(reduce(operator.or_, categories))
        return queryset

    def get_actieve_meldingen(self, queryset, name, value):
        return queryset.filter(afgesloten_op__isnull=value)

    @classmethod
    def get_filter_name(cls, field_name, lookup_expr):
        from django.db.models.constants import LOOKUP_SEP
        from django_filters.conf import settings

        """
        Combine a field name and lookup expression into a usable filter name.
        Exact lookups are the implicit default, so "exact" is stripped from the
        end of the filter name.
        """
        filter_name = LOOKUP_SEP.join([field_name, lookup_expr])

        # This also works with transformed exact lookups, such as 'date__exact'
        _default_expr = LOOKUP_SEP + settings.DEFAULT_LOOKUP_EXPR
        if filter_name.endswith(_default_expr):
            filter_name = filter_name[: -len(_default_expr)]

        return filter_name
        return f"default_{filter_name}"

    @classmethod
    def get_filters(cls):
        from collections import OrderedDict

        from django_filters.utils import get_model_field

        """
        Get all filters for the filterset. This is the combination of declared and
        generated filters.
        """

        # No model specified - skip filter generation
        if not cls._meta.model:
            return cls.declared_filters.copy()

        # Determine the filters that should be included on the filterset.
        filters = OrderedDict()
        fields = cls.get_fields()
        undefined = []

        for field_name, lookups in fields.items():
            field = get_model_field(cls._meta.model, field_name)

            # warn if the field doesn't exist.
            if field is None:
                undefined.append(field_name)

            for lookup_expr in lookups:
                filter_name = cls.get_filter_name(field_name, lookup_expr)

                # If the filter is explicitly declared on the class, skip generation
                if filter_name in cls.declared_filters:
                    filters[filter_name] = cls.declared_filters[filter_name]
                    continue

                if field is not None:
                    filters[filter_name] = cls.filter_for_field(
                        field, field_name, lookup_expr
                    )

        # Allow Meta.fields to contain declared filters *only* when a list/tuple
        if isinstance(cls._meta.fields, (list, tuple)):
            undefined = [f for f in undefined if f not in cls.declared_filters]

        if undefined:
            raise TypeError(
                "'Meta.fields' must not contain non-model field names: %s"
                % ", ".join(undefined)
            )

        # Add in declared filters. This is necessary since we don't enforce adding
        # declared filters to the 'Meta.fields' option
        filters.update(cls.declared_filters)
        filters = {f"default_{k}": v for k, v in filters.items()}
        print(filters)
        return filters

    @classmethod
    def get_declared_filters(cls, bases, attrs):
        from collections import OrderedDict

        from django_filters.filters import (
            BaseInFilter,
            BaseRangeFilter,
            BooleanFilter,
            CharFilter,
            ChoiceFilter,
            DateFilter,
            DateTimeFilter,
            DurationFilter,
            Filter,
            ModelChoiceFilter,
            ModelMultipleChoiceFilter,
            NumberFilter,
            TimeFilter,
            UUIDFilter,
        )

        filters = [
            (filter_name, attrs.pop(filter_name))
            for filter_name, obj in list(attrs.items())
            if isinstance(obj, Filter)
        ]

        # Default the `filter.field_name` to the attribute name on the filterset
        for filter_name, f in filters:
            if getattr(f, "field_name", None) is None:
                f.field_name = filter_name

        filters.sort(key=lambda x: x[1].creation_counter)

        # Ensures a base class field doesn't override cls attrs, and maintains
        # field precedence when inheriting multiple parents. e.g. if there is a
        # class C(A, B), and A and B both define 'field', use 'field' from A.
        known = set(attrs)

        def visit(name):
            known.add(name)
            return name

        base_filters = [
            (visit(name), f)
            for base in bases
            if hasattr(base, "declared_filters")
            for name, f in base.declared_filters.items()
            if name not in known
        ]
        return OrderedDict(base_filters + filters)

    class Meta:
        model = Melding
        fields = [
            "aangemaakt_op",
            "aangepast_op",
            "origineel_aangemaakt",
            "afgesloten_op",
        ]
        default_prefix = "default_"


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
        if not valid_fields == "__all_related__":
            if not context:
                context = {}
            valid_fields = super().get_valid_fields(queryset, view, context)
        else:
            valid_fields = [
                *self._retrieve_all_related_fields(
                    queryset.model._meta.get_fields(), queryset.model
                ),
                *[(key, key.title().split("__")) for key in queryset.query.annotations],
            ]
        return valid_fields


class TrigramSimilaritySearchFilter(SearchFilter):
    search_param = api_settings.SEARCH_PARAM
    template = "rest_framework/filters/search.html"
    search_title = _("Search")
    search_description = _("A search term.")

    def get_trigram_similarity(self, view, request):
        return getattr(view, "trigram_similarity", 0.3)

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.search_param, "")
        params = params.replace("\x00", "")  # strip null characters
        params = params.replace(",", " ")
        return params.split()

    def get_search_fields(self, view, request):
        """
        Search fields are obtained from the view, but the request is always
        passed to this method. Sub-classes can override this method to
        dynamically change the search fields based on request content.
        """
        return getattr(view, "search_fields", [])

    def filter_queryset(self, request, queryset, view):
        trigram_similarity = self.get_trigram_similarity(view, request)
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        # if no search_terms return
        if not search_terms:
            return queryset

        # make conditions
        conditions = []
        for search_term in search_terms:
            conditions.extend(
                [TrigramSimilarity(field, search_term) for field in search_fields]
            )

        # take the greatest similarity from all conditions
        # and annotate as similarity
        return queryset.annotate(similarity=Greatest(*conditions)).filter(
            similarity__gte=trigram_similarity
        )
