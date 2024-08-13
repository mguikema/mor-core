import logging

from django.contrib.gis.db import models
from django.db.models import (
    Avg,
    Case,
    Count,
    DurationField,
    ExpressionWrapper,
    F,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce, Concat

logger = logging.getLogger(__name__)


class StatusQuerySet(QuerySet):
    def get_veranderingen(self, params):
        from apps.aliassen.models import OnderwerpAlias
        from apps.locatie.models import Locatie
        from apps.status.models import Status

        statussen = self.all()

        sub_all_statussen = Status.objects.filter(
            melding=OuterRef("melding"), aangemaakt_op__lt=OuterRef("aangemaakt_op")
        ).order_by("melding")

        sub = sub_all_statussen.values_list("melding", flat=True)

        sub_aangemaakt_op = sub_all_statussen.order_by("-aangemaakt_op").values_list(
            "aangemaakt_op", flat=True
        )[:1]
        sub_naam = sub_all_statussen.order_by("-aangemaakt_op").values_list(
            "naam", flat=True
        )[:1]
        sum_statussen_for_meldingen = sub.annotate(
            statussen_for_melding_sum=Count("melding")
        ).values("statussen_for_melding_sum")

        # annotate with onderwerp & wijk
        locaties = Locatie.objects.filter(melding=OuterRef("pk")).order_by("-gewicht")
        onderwerpen = OnderwerpAlias.objects.filter(
            meldingen_voor_onderwerpen=OuterRef("pk")
        )
        statussen = statussen.annotate(
            onderwerp=Coalesce(
                Subquery(onderwerpen.values("response_json__name")[:1]),
                Value("Onbekend", output_field=models.JSONField()),
            )
        ).annotate(
            wijk=Coalesce(
                Subquery(locaties.values("wijknaam")[:1]),
                Value("Onbekend"),
            )
        )

        # filter out statussen whithout previous status, meaning there is no duration between only one status.
        statussen = statussen.annotate(
            status_count=Subquery(sum_statussen_for_meldingen)
        ).filter(status_count__isnull=False)

        # add previous status naam
        statussen = statussen.annotate(
            eind_status=Subquery(sub_naam), begin_status=F("naam")
        )

        # add unique combined value for averages later
        statussen = statussen.annotate(
            eind_begin_wijk_onderwerp=Concat(
                "naam",
                Value("-"),
                "eind_status",
                Value("-"),
                "onderwerp",
                Value("-"),
                "wijk",
                output_field=models.CharField(),
            )
        ).order_by("eind_begin_wijk_onderwerp")

        # add duration between begin and end status
        statussen = statussen.annotate(
            duur_seconden=ExpressionWrapper(
                F("aangemaakt_op") - Subquery(sub_aangemaakt_op),
                output_field=DurationField(),
            )
        )

        # add average duration between begin and end status
        statussen = statussen.values(
            "eind_begin_wijk_onderwerp",
            "wijk",
            "onderwerp",
            "begin_status",
            "eind_status",
        ).annotate(
            duur_seconden_gemiddeld=Avg(
                F("duur_seconden"),
                output_field=DurationField(),
            ),
            aantal=Count(F("eind_begin_wijk_onderwerp")),
        )

        return statussen.values(
            "wijk",
            "onderwerp",
            "begin_status",
            "eind_status",
            "duur_seconden_gemiddeld",
            "aantal",
        )
