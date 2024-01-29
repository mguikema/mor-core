from apps.meldingen.models import Melding
from apps.taken.models import Taakopdracht
from django.db.models import Count
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
            .values("titel", "status__naam", "melding__locaties_voor_melding__wijknaam")
            .annotate(count=Count("titel"))
            .exclude(count=0)
        )
        for taak in taken:
            c.add_metric(
                (
                    taak.get("titel"),
                    taak.get("status__naam"),
                    taak.get("melding__locaties_voor_melding__wijknaam"),
                ),
                taak.get("count"),
            )
        return c
