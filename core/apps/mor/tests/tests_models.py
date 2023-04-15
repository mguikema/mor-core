from apps.mor.managers import MeldingManager
from apps.mor.models import Melding, MeldingGebeurtenis, Signaal
from apps.status import workflow
from apps.status.models import Status
from django.db import transaction
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from model_bakery import baker


class SignaalTest(TestCase):
    def test_default_status(self):
        instance = baker.make(Signaal)
        self.assertEqual(instance.melding.status.naam, workflow.GEMELD)

    def test_melding_gebeurtenis_aangemaakt(self):
        baker.make(Signaal)
        self.assertEqual(MeldingGebeurtenis.objects.all().count(), 1)

    def test_status_aangemaakt(self):
        baker.make(Signaal)
        self.assertEqual(Status.objects.all().count(), 1)


class MeldingTransactionTest(TransactionTestCase):
    databases = {"default", "alternate"}
    DB1 = "default"
    DB2 = "alternate"
    signaal_data = {
        "origineel_aangemaakt": timezone.now().isoformat(),
    }
    status_aanpassen_data = {"status": {"naam": workflow.IN_BEHANDELING}}

    def setUp(self):
        self.melding_id = Signaal.objects.create(**self.signaal_data).melding.id

    def test_dubbele_status_verandering_serieel(self):
        with transaction.atomic(using=self.DB1):
            melding = Melding.objects.using(self.DB1).get(id=self.melding_id)
            Melding.acties.status_aanpassen(
                self.status_aanpassen_data, melding, self.DB1
            )
        with transaction.atomic(using=self.DB2):
            melding = Melding.objects.using(self.DB2).get(id=self.melding_id)
            with self.assertRaises(Status.StatusVeranderingNietToegestaan):
                Melding.acties.status_aanpassen(
                    self.status_aanpassen_data, melding, self.DB1
                )

    def test_dubbele_status_verandering_parallel(self):
        with transaction.atomic(using=self.DB1):
            melding = Melding.objects.using(self.DB1).get(id=self.melding_id)
            Melding.acties.status_aanpassen(
                self.status_aanpassen_data, melding, self.DB1
            )
            with transaction.atomic(using=self.DB2):
                melding = Melding.objects.using(self.DB2).get(id=self.melding_id)
                with self.assertRaises(MeldingManager.MeldingInGebruik):
                    Melding.acties.status_aanpassen(
                        self.status_aanpassen_data, melding, self.DB2
                    )
