import logging

from django.contrib.gis.db import models
from django.db.models import Count, OuterRef, QuerySet, Subquery, Value
from django.db.models.functions import Coalesce, Concat

logger = logging.getLogger(__name__)


class MeldingQuerySet(QuerySet):
    def get_aantallen(self):
        from apps.aliassen.models import OnderwerpAlias
        from apps.locatie.models import Locatie

        locaties = Locatie.objects.filter(melding=OuterRef("pk")).order_by("-gewicht")
        onderwerpen = OnderwerpAlias.objects.filter(
            meldingen_voor_onderwerpen=OuterRef("pk")
        )
        meldingen = self.all()

        logger.info(f"filtered meldingen count: {meldingen.count()}")

        meldingen = meldingen.annotate(
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
        meldingen = meldingen.annotate(
            onderwerp_wijk=Concat(
                "onderwerp", Value("-"), "wijk", output_field=models.CharField()
            )
        )
        meldingen = (
            meldingen.values("onderwerp_wijk", "onderwerp", "wijk")
            .order_by("onderwerp_wijk")
            .annotate(count=Count("onderwerp_wijk"))
            .values("count", "onderwerp", "wijk")
        )
        meldingen_count = [m.get("count") for m in meldingen]
        logger.info(f"meldingen count sum: {sum(meldingen_count)}")
        return meldingen
