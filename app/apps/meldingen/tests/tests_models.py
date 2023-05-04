import requests_mock
from apps.meldingen.managers import MeldingManager
from apps.meldingen.models import (
    Melding,
    MeldingContext,
    MeldingGebeurtenis,
    OnderwerpAlias,
    Signaal,
)
from apps.meldingen.serializers import MeldingGebeurtenisStatusSerializer
from apps.status import workflow
from apps.status.models import Status
from django.db import transaction
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from model_bakery import baker


class SignaalTest(TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        m.get("http://mock_url", json={}, status_code=200)
        onderwerp_alias = baker.make(OnderwerpAlias, bron_url="http://mock_url")
        baker.make(
            MeldingContext, onderwerpen=OnderwerpAlias.objects.all(), slug="slug"
        )
        self.instance = baker.make(Signaal, onderwerpen=[onderwerp_alias.bron_url])

    def test_default_status(self):
        self.assertEqual(self.instance.melding.status.naam, workflow.GEMELD)

    def test_melding_gebeurtenis_aangemaakt(self):
        self.assertEqual(MeldingGebeurtenis.objects.all().count(), 1)

    def test_status_aangemaakt(self):
        self.assertEqual(Status.objects.all().count(), 1)


class MeldingTransactionTest(TransactionTestCase):
    databases = {"default", "alternate"}
    DB1 = "default"
    DB2 = "alternate"
    signaal_data = {
        "origineel_aangemaakt": timezone.now().isoformat(),
        "onderwerpen": ["http://mock_url"],
    }
    status_aanpassen_data = {"status": {"naam": workflow.AFGEHANDELD}}

    @requests_mock.Mocker()
    def setUp(self, m):
        m.get("http://mock_url", json={}, status_code=200)
        baker.make(OnderwerpAlias, bron_url="http://mock_url")
        baker.make(
            MeldingContext, onderwerpen=OnderwerpAlias.objects.all(), slug="slug"
        )
        self.melding_id = Signaal.objects.create(**self.signaal_data).melding.id
        data = {"melding": self.melding_id}
        data.update(self.status_aanpassen_data)
        data["status"]["melding"] = self.melding_id

        self.serializer = MeldingGebeurtenisStatusSerializer(data=data)
        self.serializer.is_valid()

    def test_dubbele_status_verandering_serieel(self):
        with transaction.atomic(using=self.DB1):
            melding = Melding.objects.using(self.DB1).get(id=self.melding_id)
            Melding.acties.status_aanpassen(self.serializer, melding, self.DB1)
        with transaction.atomic(using=self.DB2):
            melding = Melding.objects.using(self.DB2).get(id=self.melding_id)
            with self.assertRaises(Status.StatusVeranderingNietToegestaan):
                Melding.acties.status_aanpassen(self.serializer, melding, self.DB1)

    def test_dubbele_status_verandering_parallel(self):
        with transaction.atomic(using=self.DB1):
            melding = Melding.objects.using(self.DB1).get(id=self.melding_id)
            Melding.acties.status_aanpassen(self.serializer, melding, self.DB1)
            with transaction.atomic(using=self.DB2):
                melding = Melding.objects.using(self.DB2).get(id=self.melding_id)
                with self.assertRaises(MeldingManager.MeldingInGebruik):
                    Melding.acties.status_aanpassen(self.serializer, melding, self.DB2)
