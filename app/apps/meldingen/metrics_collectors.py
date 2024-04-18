from apps.applicaties.models import Applicatie
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
    locatie_subquery = (
        Locatie.objects.filter(melding=OuterRef("melding"))
        .order_by("-gewicht", "-aangemaakt_op")
        .distinct()
    )

    def create_taaktype_threshold_dict(self):
        max_days_threshold_dict = {}
        unique_taaktypes = (
            Taakopdracht.objects.values_list("taaktype", flat=True)
            .distinct()
            .order_by("taaktype")
        )
        for taaktype_url in unique_taaktypes:
            taakapplicatie = Applicatie.vind_applicatie_obv_uri(taaktype_url)
            taaktype_data = taakapplicatie.fetch_taaktype_data(taaktype_url)
            max_days_threshold_dict[taaktype_url] = (
                taaktype_data.get("threshold", 3) if taaktype_data else 3
            )
        return max_days_threshold_dict

    def annotate_thresholds(self, queryset):
        return queryset.annotate(
            threshold=Case(
                *[
                    When(taaktype=tt, then=Value(threshold))
                    for tt, threshold in self.taak_type_threshold_dict.items()
                ],
                default=Value(3),
            )
        )

    def annotate_highest_weight_wijk(self, queryset):
        return queryset.annotate(
            highest_weight_wijk=Coalesce(
                Subquery(self.locatie_subquery.values("wijknaam")[:1]),
                Value("Onbekend"),
            ),
        )

    def collect(self):
        self.taak_type_threshold_dict = self.create_taaktype_threshold_dict()
        self.annotated_threshold_taken = self.annotate_thresholds(
            Taakopdracht.objects.all()
        )

        # Meldingen metrics
        yield self.collect_melding_metrics()

        # Taak total metrics
        yield self.collect_taak_metrics()

        # Taken langer dan taaktype threshold open
        yield self.collect_taken_over_threshold_metrics()

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
                "over_threshold",
                "threshold",
            ],
        )
        # Annotate the threshold value for each taak
        taken_with_locatie = (
            self.annotate_highest_weight_wijk(self.annotated_threshold_taken)
            .annotate(
                over_threshold=Count(
                    Case(
                        When(
                            ~Q(status__naam="voltooid"),  # Exclude 'voltooid' status
                            afgesloten_op__isnull=True,
                            aangemaakt_op__lte=timezone.now()
                            - timezone.timedelta(days=1) * F("threshold"),
                            then=1,
                        ),
                    )
                ),
            )
            .values(
                "titel",
                "status__naam",
                "highest_weight_wijk",
                "over_threshold",
                "threshold",
            )
            .order_by("titel")
            .annotate(total_count=Count("titel"))
        )

        for taak in taken_with_locatie:
            c.add_metric(
                (
                    taak["titel"],
                    taak["status__naam"],
                    taak["highest_weight_wijk"],
                    str(taak["over_threshold"]),
                    str(taak["threshold"]),
                ),
                taak["total_count"],
            )

        return c

    def collect_taak_duur_metrics(self):
        c = CounterMetricFamily(
            "morcore_taken_duur_openstaand",
            "Taak duur openstaand",
            labels=["taaktype", "status", "wijk"],
        )
        taken = (
            self.annotate_highest_weight_wijk(Taakopdracht.objects)
            .values(
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
            labels=["taaktype", "wijk", "threshold"],
        )

        openstaande_taken = self.annotated_threshold_taken.filter(
            afgesloten_op__isnull=True,
            aangemaakt_op__lte=timezone.now()
            - timezone.timedelta(days=1) * F("threshold"),
        ).exclude(status__naam="voltooid")

        openstaande_taken_per_wijk_taaktype = (
            self.annotate_highest_weight_wijk(openstaande_taken)
            .values("titel", "highest_weight_wijk", "threshold")
            .order_by("titel")
            .annotate(count=Count("titel"))
        )

        for taak in openstaande_taken_per_wijk_taaktype:
            c.add_metric(
                (
                    taak.get("titel"),
                    taak.get("highest_weight_wijk"),
                    str(taak.get("threshold")),
                ),
                taak.get("count"),
            )

        return c
