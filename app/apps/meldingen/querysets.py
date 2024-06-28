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
from django.db.models.functions import Coalesce

logger = logging.getLogger(__name__)


class MeldingQuerySet(QuerySet):
    def get_aantallen(self):
        from apps.aliassen.models import OnderwerpAlias
        from apps.locatie.models import Locatie

        locaties = Locatie.objects.filter(pk=OuterRef("pk")).order_by("-gewicht")
        onderwerpen = OnderwerpAlias.objects.filter(pk=OuterRef("pk"))

        meldingen = (
            self.annotate(
                onderwerp=Coalesce(
                    Subquery(onderwerpen.values("response_json__name")[:1]),
                    Value("Onbekend", output_field=models.JSONField()),
                    output_field=models.JSONField(),
                )
            )
            .annotate(
                wijk=Coalesce(
                    Subquery(locaties.values("wijknaam")[:1]),
                    Value("Onbekend"),
                )
            )
            .values("onderwerp", "wijk")
            .annotate(count=Count("onderwerp"))
            .values("count", "onderwerp", "wijk")
        )
        logger.info(f"all meldingen: {self.count()}")
        meldingen_count = [m.get("count") for m in meldingen]
        logger.info(f"meldingen count sum: {sum(meldingen_count)}")
        return meldingen
