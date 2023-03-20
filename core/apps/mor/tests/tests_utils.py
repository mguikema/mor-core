from apps.mor.models import Bron, Signaal
from apps.mor.utils import get_q_objects_from_qs
from django.test import TestCase
from django.utils import timezone


class QueryStringFilter(TestCase):
    def test_get_not_found(self):
        b = Bron.objects.create(naam="bron")
        # s = Signaal.objects.create(
        #     **{
        #         "origineel_aangemaakt": timezone.now(),
        #         "bron": b,
        #         "tekst": "mock tekst bijzonder",
        #         "meta": {
        #             "vak": "A",
        #             "grafnummer": "42",
        #             "begraafplaats": "mock_begraafplaats",
        #         },
        #     }
        # )
        # print(s)

        query = "tekst__contains=ock&tekst__contains=ijzonz&meta__key1__contains=ey1"

        new_signaal = {
            "origineel_aangemaakt": timezone.now(),
            "bron": b,
            "tekst": "mock tekst bijzonder",
            "meta": {
                "vak": "A",
                "grafnummer": "42",
                "begraafplaats": "mock_begraafplaats",
            },
        }

        # n = SimpleNamespace(**new_signaal)
        # def set_locals(d):
        # for k, v in d.items():
        # exec(f'{k} = "{v}"')
        # print("locals()")
        # print(locals())
        # print(origineel_aangemaakt)
        # set_locals(new_signaal)
        ss = Signaal(**new_signaal)
        # meta = {}
        # from box import Box
        # new_signaal = {k: Box(v) if type(v) is dict else v for k, v in new_signaal.items()}
        # query = "meta__begraafplaats={meta.begraafplaats}&meta__grafnummer={meta.grafnummer}&meta__vak={meta.vak}".format(**new_signaal)
        query = ss.parse_querystring(
            "meta__begraafplaats={meta.begraafplaats}&meta__grafnummer={meta.grafnummer}&meta__vak={meta.vak}&bron__id={bron.id}"
        )
        print(query)
        q_objects = get_q_objects_from_qs(query)
        # print(q_objects)
        sq = Signaal.objects.filter(q_objects)

        # print(sq)
        # sq = Signaal.objects.filter(Q(("tekst__contains",("ock",))))
        # print(sq)

        self.assertEqual(sq.count(), 1)
