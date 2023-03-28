import copy

from apps.mor.utils import get_q_objects_from_qs
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet


class SignaalQuerySet(QuerySet):
    def filter_to_get_melding(self, signaal_instance):
        try:
            ontdubbelregel = signaal_instance.bron.ontdubbelregel
        except Exception as e:
            print(e)
            return
        formatted_ontdubbelregel = signaal_instance.parse_querystring(ontdubbelregel)
        try:
            result = self.filter(
                get_q_objects_from_qs(formatted_ontdubbelregel), melding__isnull=False
            )
        except Exception as e:
            print(e)
            return
        if result:
            print("Maybe check to see if all of these Signalen share the same Melding")
            return result.first.melding
        return


class MeldingQuerySet(QuerySet):
    def create_from_signaal(self, signaal):
        from apps.locatie.models import Graf
        from apps.mor.models import Melding

        data = copy.deepcopy(signaal.ruwe_informatie)
        meta_uitgebreid = data.pop("labels", {})
        melding = Melding()
        melding.origineel_aangemaakt = signaal.origineel_aangemaakt
        melding.omschrijving_kort = data.get("toelichting", "")[:200]
        melding.omschrijving = data.get("toelichting")
        melding.meta = data
        melding.meta_uitgebreid = meta_uitgebreid
        melding.onderwerp = signaal.onderwerp
        melding.save()

        mct = ContentType.objects.get_for_model(Melding)
        Graf.objects.create(
            **{
                "object_id": melding.pk,
                "content_type": mct,
                "plaatsnaam": "Rotterdam",
                "begraafplaats": data.get("begraafplaats"),
                "grafnummer": data.get("grafnummer"),
                "vak": data.get("vak"),
            }
        )

        return melding
