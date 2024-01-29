from apps.locatie.models import Locatie
from apps.meldingen.models import Melding
from apps.taken.models import Taakopdracht
from django.db.models import Count, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from prometheus_client.core import CounterMetricFamily


class CustomCollector(object):
    def collect(self):
        # Meldingen metrics
        melding_metrics = self.collect_melding_metrics()
        yield melding_metrics

        # Taak metrics
        taak_metrics = self.collect_taak_metrics()
        yield taak_metrics

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

    # Wijk toevoegen, via melding - locatie
    def collect_taak_metrics(self):
        c = CounterMetricFamily(
            "morcore_taken_total",
            "Taak aantallen",
            labels=["taaktype", "status", "wijk"],
        )
        taken = (
            Taakopdracht.objects.order_by("titel")
            .annotate(
                highest_weight_wijk=Coalesce(
                    Subquery(
                        Locatie.objects.filter(
                            melding=OuterRef("melding"),
                        )
                        .order_by("-gewicht")
                        .values("wijknaam")[:1]
                    ),
                    Value("Onbekend"),
                ),
            )
            .values("titel", "status__naam", "highest_weight_wijk")
            .annotate(count=Count("titel"))
            .exclude(count=0)
        )
        for taak in taken:
            c.add_metric(
                (
                    taak.get("titel"),
                    taak.get("status__naam"),
                    taak.get("highest_weight_wijk"),
                ),
                taak.get("count"),
            )
        return c
