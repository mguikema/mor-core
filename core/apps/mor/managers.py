from django.contrib.gis.db import models
from django.db import transaction
from django.dispatch import Signal as DjangoSignal

status_aanpassen = DjangoSignal()


class MeldingManager(models.Manager):
    def status_aanpassen(self, data, melding):
        from apps.mor.models import Melding, MeldingGebeurtenis
        from apps.status.models import Status

        with transaction.atomic():
            locked_melding = Melding.objects.select_for_update(nowait=True).get(
                pk=melding.pk
            )
            vorige_status = melding.status
            status_instance = Status(
                melding=melding, naam=data.get("status", {}).get("naam")
            )
            status_instance.save()
            melding_gebeurtenis = MeldingGebeurtenis(
                **dict(
                    melding=locked_melding,
                    status=status_instance,
                    omschrijving=data.get("omschrijving"),
                )
            )
            melding_gebeurtenis.save()
            locked_melding.status = status_instance
            locked_melding.save()
            transaction.on_commit(
                lambda: status_aanpassen.send_robust(
                    sender=self.__class__,
                    signal_obj=locked_melding,
                    status=status_instance,
                    prev_status=vorige_status,
                )
            )
