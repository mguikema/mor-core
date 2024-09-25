import logging

from django.contrib.gis.db import models
from django.db.models import Count, OuterRef, QuerySet, Subquery, Value
from django.db.models.functions import Coalesce, Concat

logger = logging.getLogger(__name__)


class TaakopdrachtQuerySet(QuerySet):
    def taaktype_aantallen_per_melding(self, querystring):
        from apps.aliassen.models import OnderwerpAlias
        from apps.locatie.models import Locatie

        inclusief_melding = querystring.get("inclusief-melding", False)

        locaties = Locatie.objects.filter(melding=OuterRef("melding")).order_by(
            "-gewicht"
        )
        onderwerpen = OnderwerpAlias.objects.filter(
            meldingen_voor_onderwerpen=OuterRef("melding")
        )
        taakopdrachten = self.all()

        logger.info(
            f"aantal meldingen: {taakopdrachten.values('melding').order_by().distinct().count()}"
        )

        taakopdrachten = taakopdrachten.annotate(
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
        logger.info(f"taakopdrachten count: {taakopdrachten.count()}")

        taakopdrachten = (
            taakopdrachten.annotate(
                melding_taaktype=Concat(
                    "melding", Value("-"), "taaktype", output_field=models.CharField()
                )
            )
            .values("melding_taaktype", "titel", "wijk", "onderwerp")
            .order_by()
        )
        taakopdrachten = taakopdrachten.annotate(
            taaktype_melding_aantal=Count("melding_taaktype")
        )

        taakopdrachten = (
            taakopdrachten.annotate(
                onderwerp_wijk_taaktype_aantal=Concat(
                    "onderwerp",
                    Value("-"),
                    "wijk",
                    Value("-"),
                    "taaktype",
                    Value("-"),
                    "taaktype_melding_aantal",
                    output_field=models.CharField(),
                )
            )
            .values(
                "onderwerp_wijk_taaktype_aantal",
                "taaktype",
                "wijk",
                "onderwerp",
                "taaktype_melding_aantal",
                "melding",
                "melding__uuid",
                "titel",
            )
            .order_by()
        )

        logger.info(f"taakopdrachten count: {taakopdrachten.count()}")

        taakopdrachten = list(
            {
                taakopdracht.get("onderwerp_wijk_taaktype_aantal"): {
                    "wijk": taakopdracht.get("wijk"),
                    "onderwerp": taakopdracht.get("onderwerp"),
                    "taaktype": taakopdracht.get("taaktype"),
                    "titel": taakopdracht.get("titel"),
                    "aantal_per_melding": taakopdracht.get("taaktype_melding_aantal"),
                    "melding_aantal": len(
                        [
                            to
                            for to in taakopdrachten
                            if to.get("onderwerp_wijk_taaktype_aantal")
                            == taakopdracht.get("onderwerp_wijk_taaktype_aantal")
                        ]
                    ),
                    "meldingen": [
                        to.get("melding__uuid")
                        for to in taakopdrachten
                        if to.get("onderwerp_wijk_taaktype_aantal")
                        == taakopdracht.get("onderwerp_wijk_taaktype_aantal")
                    ]
                    if inclusief_melding
                    else [],
                }
                for taakopdracht in taakopdrachten
            }.values()
        )

        logger.info(f"taakopdrachten len: {len(taakopdrachten)}")
        return taakopdrachten
