from apps.meldingen.models import Melding
from django.db.models import Count
from prometheus_client.core import CounterMetricFamily


class CustomCollector(object):
    def collect(self):
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
        yield c
