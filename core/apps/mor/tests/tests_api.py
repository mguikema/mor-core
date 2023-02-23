import io
import os

from apps.mor.models import (
    Bijlage,
    Melding,
    MeldingGebeurtenis,
    MeldingGebeurtenisType,
    TaakApplicatie,
)
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from utils.unittest_helpers import GenericAPITestCase


class TaakApplicatieApiTest(APITestCase, GenericAPITestCase):
    url_basename = "app:taak_applicatie"
    model_cls = TaakApplicatie
    mock_instance = {"naam": "mock"}


class BijlageApiTest(APITestCase):
    def test_get_not_found(self):
        url = reverse("app:bijlage-detail", kwargs={"pk": 99})

        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_with_file(self):
        url = reverse("app:bijlage-list")
        melding_gebeurtenis = baker.make(MeldingGebeurtenis)
        client = APIClient()
        file = "tekst.rtf"
        base_dir = os.path.dirname(os.path.realpath(__file__))
        with open(f"{base_dir}/bestanden/{file}", "rb") as fp:
            fio = io.FileIO(fp.fileno())
            fio.name = fp.name
            data = {
                "melding_gebeurtenis": melding_gebeurtenis.id,
                "bestand": fio,
            }

            response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("is_afbeelding"), False)

    def test_create_with_image(self):
        url = reverse("app:bijlage-list")
        melding_gebeurtenis = baker.make(MeldingGebeurtenis)
        client = APIClient()
        file = "afbeelding.jpg"
        base_dir = os.path.dirname(os.path.realpath(__file__))
        with open(f"{base_dir}/bestanden/{file}", "rb") as fp:
            fio = io.FileIO(fp.fileno())
            fio.name = fp.name
            data = {
                "melding_gebeurtenis": melding_gebeurtenis.id,
                "bestand": fio,
            }
            response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("is_afbeelding"), True)

    def test_get(self):
        instance = baker.make(Bijlage, _create_files=True)
        url = reverse("app:bijlage-detail", kwargs={"pk": instance.pk})

        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list(self):
        baker.make(Bijlage, _quantity=2, _create_files=True)

        url = reverse("app:bijlage-list")

        client = APIClient()
        response = client.get(url)
        data = response.json()

        self.assertEqual(len(data["results"]), 2)


class MeldingGebeurtenisTypeApiTest(APITestCase):
    def test_get_not_found(self):
        url = reverse("app:melding_gebeurtenis_type-detail", kwargs={"pk": 99})

        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        url = reverse("app:melding_gebeurtenis_type-list")
        melding_gebeurtenis = baker.make(MeldingGebeurtenis)
        client = APIClient()

        data = {
            "melding_gebeurtenis": melding_gebeurtenis.id,
            "type_naam": MeldingGebeurtenisType.TypeNaamOpties.META_DATA_WIJZIGING,
        }

        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get(self):
        instance = baker.make(MeldingGebeurtenisType)
        url = reverse("app:melding_gebeurtenis_type-detail", kwargs={"pk": instance.pk})

        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list(self):
        baker.make(MeldingGebeurtenisType, _quantity=2, _create_files=True)

        url = reverse("app:melding_gebeurtenis_type-list")

        client = APIClient()
        response = client.get(url)
        data = response.json()

        self.assertEqual(len(data["results"]), 2)


class MeldingGebeurtenisApiTest(APITestCase):
    def test_get_not_found(self):
        url = reverse("app:melding_gebeurtenis-detail", kwargs={"pk": 99})

        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create(self):
        url = reverse("app:melding_gebeurtenis-list")
        melding = baker.make(Melding)
        client = APIClient()

        data = {
            "melding": melding.id,
        }

        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get(self):
        instance = baker.make(MeldingGebeurtenis)
        url = reverse("app:melding_gebeurtenis-detail", kwargs={"pk": instance.pk})

        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list(self):
        baker.make(MeldingGebeurtenis, _quantity=2)

        url = reverse("app:melding_gebeurtenis-list")

        client = APIClient()
        response = client.get(url)
        data = response.json()

        self.assertEqual(len(data["results"]), 2)


class MeldingApiTest(APITestCase):
    def test_get_not_found(self):
        url = reverse("app:melding-detail", kwargs={"pk": 99})

        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_met_taak_applicatie(self):
        url = reverse("app:melding-list")
        taak_applicatie = baker.make(TaakApplicatie)
        client = APIClient()

        data = {
            "taak_applicaties": [taak_applicatie.id],
        }

        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_zonder_taak_applicatie(self):
        url = reverse("app:melding-list")
        client = APIClient()
        response = client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get(self):
        instance = baker.make(Melding)
        url = reverse("app:melding-detail", kwargs={"pk": instance.pk})

        client = APIClient()
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_list(self):
        baker.make(Melding, _quantity=2)

        url = reverse("app:melding-list")

        client = APIClient()
        response = client.get(url)
        data = response.json()

        self.assertEqual(len(data["results"]), 2)
