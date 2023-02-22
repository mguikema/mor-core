from apps.mor.models import TaakApplicatie
from rest_framework.test import APITestCase
from utils.unittest_helpers import GenericAPITestCase


class TaakApplicatieApiTest(APITestCase, GenericAPITestCase):
    url_basename = "app:taak_applicatie"
    model_cls = TaakApplicatie
    mock_instance = {"naam": "mock"}


# class BijlageApiTest(APITestCase):
#     incident_gebeurtenis = None
#     melding = None
#     url_basename = ""

#     def setUp(self):
#         management.call_command("flush", verbosity=0, interactive=False)
#         incident_gebeurtenis = baker.make(MeldingGebeurtenis)
#         self.melding = baker.make(Melding)
#         super().setUp()

#     def test_create(self):
#         url = reverse(f"{self.url_basename}-list")

#         client = APIClient()
#         response = client.post(url, self.mock_instance)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
