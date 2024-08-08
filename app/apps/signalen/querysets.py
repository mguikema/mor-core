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


class SignaalQuerySet(QuerySet):
    def get_aantallen(self):
        from apps.aliassen.models import OnderwerpAlias
        from apps.locatie.models import Locatie

        locaties = Locatie.objects.filter(signaal=OuterRef("pk")).order_by("-gewicht")
        onderwerpen = OnderwerpAlias.objects.filter(
            signalen_voor_onderwerpen=OuterRef("pk")
        )
        signalen = self.all()

        logger.info(f"filtered signalen count: {signalen.count()}")

        signalen = signalen.annotate(
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
        signalen = signalen.annotate(
            onderwerp_wijk=Concat(
                "onderwerp", Value("-"), "wijk", output_field=models.CharField()
            )
        )
        signalen = (
            signalen.values("onderwerp_wijk", "onderwerp", "wijk")
            .order_by("onderwerp_wijk")
            .annotate(count=Count("onderwerp_wijk"))
            .values("count", "onderwerp", "wijk")
        )
        signaal_count = [m.get("count") for m in signalen]
        logger.info(f"signaal count sum: {sum(signaal_count)}")
        return signalen
