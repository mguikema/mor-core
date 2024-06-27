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


class SignaalQuerySet(QuerySet):
    def get_aantallen(self):
        from apps.locatie.models import Locatie

        locaties = Locatie.objects.filter(signaal=OuterRef("pk")).order_by("-gewicht")
        signalen = (
            self.values(
                onderwerp=F("onderwerpen__response_json__name"),
            )
            .filter(onderwerp__isnull=False)
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
        return signalen
