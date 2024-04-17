from apps.locatie.models import Locatie
from apps.meldingen.models import Melding
from apps.taken.models import Taakopdracht
from django.db.models import (
    Avg,
    Case,
    Count,
    DurationField,
    ExpressionWrapper,
    F,
    OuterRef,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce
from django.utils import timezone
from prometheus_client.core import CounterMetricFamily


def duration_to_seconds(duration):
    """Converts a duration string to seconds."""
    return duration.total_seconds() if duration else None


class CustomCollector(object):
    locatie_subquery = (
        Locatie.objects.filter(melding=OuterRef("melding"))
        .order_by("-gewicht", "-aangemaakt_op")
        .distinct()
    )

    def collect(self):
        # Meldingen metrics
        melding_metrics = self.collect_melding_metrics()
        yield melding_metrics

        # Taak total metrics
        taak_total_metrics = self.collect_taak_metrics()
        yield taak_total_metrics

        # Taak duur openstaand metrics
        taak_duur_openstaand_metrics = self.collect_taak_duur_metrics()
        yield taak_duur_openstaand_metrics

    def collect_melding_metrics(self):
        c = CounterMetricFamily(
            "morcore_meldingen_total",
            "Melding aantallen",
            labels=["onderwerp", "status"],
        )
        meldingen = (
            Melding.objects.order_by("onderwerpen")
            .values("onderwerpen__response_json__name", "status__naam")
            .annotate(count=Count("onderwerpen"))
            .exclude(count=0)
        )
        for m in meldingen:
            c.add_metric(
                [
                    m.get("onderwerpen__response_json__name"),
                    m.get("status__naam"),
                ],
                m.get("count"),
            )
        return c

    def collect_taak_metrics(self):
        c = CounterMetricFamily(
            "morcore_taken_total",
            "Taak aantallen",
            labels=["taaktype", "status", "wijk"],
        )

        taken_with_locatie = (
            Taakopdracht.objects.order_by("titel")
            .annotate(
                highest_weight_wijk=Coalesce(
                    Subquery(self.locatie_subquery.values("wijknaam")[:1]),
                    Value("Onbekend"),
                ),
            )
            .values("titel", "status__naam", "highest_weight_wijk")
            .annotate(count=Count("titel"))
            .exclude(count=0)
        )
        for taak in taken_with_locatie:
            c.add_metric(
                (
                    taak.get("titel"),
                    taak.get("status__naam"),
                    taak.get("highest_weight_wijk"),
                ),
                taak.get("count"),
            )
        return c

    def collect_taak_duur_metrics(self):
        c = CounterMetricFamily(
            "morcore_taken_duur_openstaand",
            "Taak duur openstaand",
            labels=["taaktype", "status", "wijk"],
        )
        taken = (
            Taakopdracht.objects.order_by("titel")
            .annotate(
                highest_weight_wijk=Coalesce(
                    Subquery(self.locatie_subquery.values("wijknaam")[:1]),
                    Value("Onbekend"),
                ),
            )
            .values(
                "titel",
                "status__naam",
                "highest_weight_wijk",
            )
            .annotate(
                avg_openstaand=Avg(
                    Case(
                        When(
                            afgesloten_op__isnull=False,
                            aangemaakt_op__isnull=False,
                            afhandeltijd__isnull=False,
                            then=F("afhandeltijd"),
                        ),
                        default=ExpressionWrapper(
                            timezone.now() - F("aangemaakt_op"),
                            output_field=DurationField(),
                        ),
                        output_field=DurationField(),
                    ),
                ),
            )
        )

        for taak in taken:
            if avg_openstaand_duration := taak.get("avg_openstaand"):
                avg_openstaand_seconds = avg_openstaand_duration.total_seconds()

                c.add_metric(
                    (
                        taak.get("titel"),
                        taak.get("status__naam"),
                        taak.get("highest_weight_wijk"),
                    ),
                    avg_openstaand_seconds,
                )
        return c
