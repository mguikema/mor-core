from apps.applicaties.models import Applicatie
from apps.locatie.models import Locatie
from apps.meldingen.models import Melding
from apps.taken.models import Taakopdracht
from django.conf import settings
from django.db.models import (
    Avg,
    Case,
    Count,
    DurationField,
    ExpressionWrapper,
    F,
    OuterRef,
    Q,
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
    def __init__(self):
        self.taak_type_threshold_list = self.create_taaktype_threshold_list()
        self.annotated_wijken_taken = self.annotate_highest_weight_wijk(
            Taakopdracht.objects.all()
        )
        self.annotated_threshold_taken = self.annotate_thresholds(
            self.annotated_wijken_taken
        )

    def create_taaktype_threshold_list(self):
        taak_type_threshold_list = []
        taakapplicatie = Applicatie.vind_applicatie_obv_uri(
            settings.TAAKTYPE_APPLICATIE_URL
        )
        taaktype_data = taakapplicatie.taaktypes_halen()
        for taaktype in taaktype_data:
            taak_type_threshold_list.append(
                {
                    "taaktype_url": taaktype["_links"].get("self", ""),
                    "threshold": taaktype.get("threshold", 3),
                    "titel": taaktype.get("omschrijving", ""),
                }
            )
        return taak_type_threshold_list

    def annotate_thresholds(self, queryset):
        return queryset.annotate(
            threshold=Case(
                *[
                    When(
                        taaktype=taaktype.get("taaktype_url", ""),
                        then=Value(taaktype.get("threshold", 3)),
                    )
                    for taaktype in self.taak_type_threshold_list
                ],
                default=Value(3),
            )
        )

    def annotate_highest_weight_wijk(self, queryset):
        locatie_subquery = (
            Locatie.objects.filter(melding=OuterRef("melding"))
            .order_by("-gewicht", "-aangemaakt_op")
            .distinct()
        )
        return queryset.annotate(
            highest_weight_wijk=Coalesce(
                Subquery(locatie_subquery.values("wijknaam")[:1]),
                Value("Onbekend"),
            ),
        )

    def collect(self):
        # Meldingen metrics
        yield self.collect_melding_metrics()

        # Taak total metrics
        yield self.collect_taak_metrics()

        # Taaktype threshold
        yield self.collect_taaktype_threshold_metrics()

        # Taken langer dan taaktype threshold open
        yield self.collect_taken_over_threshold_metrics()

        # Taken minder langer dan taaktype threshold open
        yield self.collect_taken_onder_threshold_metrics()

        # Taak duur openstaand metrics
        yield self.collect_taak_duur_metrics()

    def collect_melding_metrics(self):
        c = CounterMetricFamily(
            "morcore_meldingen_total",
            "Melding aantallen",
            labels=["onderwerp", "status"],
        )
        meldingen = (
            Melding.objects.values("onderwerpen__response_json__name", "status__naam")
            .order_by("onderwerpen")
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
            labels=[
                "taaktype",
                "status",
                "wijk",
            ],
        )

        total_taken = (
            self.annotated_wijken_taken.values(
                "titel", "status__naam", "highest_weight_wijk"
            )
            .order_by("titel")
            .annotate(count=Count("titel"))
        )

        for taak in total_taken:
            c.add_metric(
                (
                    taak["titel"],
                    taak["status__naam"],
                    taak["highest_weight_wijk"],
                ),
                taak["count"],
            )

        return c

    def collect_taak_duur_metrics(self):
        c = CounterMetricFamily(
            "morcore_taken_duur_openstaand",
            "Taak duur openstaand",
            labels=["taaktype", "status", "wijk"],
        )
        taken = (
            self.annotated_wijken_taken.values(
                "titel",
                "status__naam",
                "highest_weight_wijk",
            )
            .order_by("titel")
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

    def collect_taken_over_threshold_metrics(self):
        c = CounterMetricFamily(
            "morcore_taken_over_threshold",
            "Aantal taken langer open dan de threshold van het taaktype per wijk en taaktype",
            labels=["taaktype", "wijk"],
        )
        threshold_taken = (
            self.annotated_threshold_taken.filter(
                ~Q(status__naam="voltooid"),
                afgesloten_op__isnull=True,
                aangemaakt_op__lte=timezone.now()
                - timezone.timedelta(days=1) * F("threshold"),
            )
            .values("titel", "highest_weight_wijk")
            .order_by("titel")
            .annotate(count=Count("titel"))
        )

        for taak in threshold_taken:
            c.add_metric(
                (
                    taak.get("titel"),
                    taak.get("highest_weight_wijk"),
                ),
                taak.get("count"),
            )

        return c

    def collect_taken_onder_threshold_metrics(self):
        c = CounterMetricFamily(
            "morcore_taken_onder_threshold",
            "Aantal taken minder lang open dan de threshold van het taaktype per wijk en taaktype",
            labels=["taaktype", "wijk"],
        )

        taken = (
            self.annotated_threshold_taken.filter(
                ~Q(status__naam="voltooid"),
                afgesloten_op__isnull=True,
                aangemaakt_op__gt=timezone.now()
                - timezone.timedelta(days=1) * F("threshold"),
            )
            .values("titel", "highest_weight_wijk")
            .order_by("titel")
            .annotate(count=Count("titel"))
        )

        for taak in taken:
            c.add_metric(
                (
                    taak.get("titel"),
                    taak.get("highest_weight_wijk"),
                ),
                taak.get("count"),
            )

        return c

    def collect_taaktype_threshold_metrics(self):
        c = CounterMetricFamily(
            "morcore_taaktype_threshold",
            "De threshold in dagen van elk taaktype",
            labels=["taaktype", "taaktype_url"],
        )

        for taaktype in self.taak_type_threshold_list:
            taaktype_url = taaktype.get("taaktype_url", "")
            threshold = taaktype.get("threshold", 3)
            titel = taaktype.get("titel", "")

            c.add_metric((titel, taaktype_url), threshold)

        return c
