import copy

from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.db import OperationalError, transaction
from django.dispatch import Signal as DjangoSignal

aangemaakt = DjangoSignal()
status_aangepast = DjangoSignal()


class MeldingManager(models.Manager):
    class StatusVeranderingNietToegestaan(Exception):
        pass

    class MeldingContextInGebruik(Exception):
        pass

    class MeldingInGebruik(Exception):
        pass

    class MeldingContextOnderwerpNietGevonden(Exception):
        pass

    def aanmaken(self, signaal, db="default"):
        from apps.locatie.models import Graf
        from apps.mor.models import Melding, MeldingContext, MeldingGebeurtenis
        from apps.status.models import Status

        if signaal.melding:
            return signaal.melding

        with transaction.atomic():
            try:
                melding_context = (
                    MeldingContext.objects.using(db)
                    .select_for_update(nowait=True)
                    .filter(onderwerpen__contains=signaal.onderwerpen)
                    .first()
                )
            except OperationalError:
                raise MeldingManager.MeldingContextInGebruik

            data = copy.deepcopy(signaal.ruwe_informatie)
            meta_uitgebreid = data.pop("labels", {})
            melding = Melding()

            melding.melding_context = melding_context

            status_instance = Status()
            melding.origineel_aangemaakt = signaal.origineel_aangemaakt
            melding.omschrijving_kort = data.get("toelichting", "")[:200]
            melding.omschrijving = data.get("toelichting")
            melding.meta = data
            melding.meta_uitgebreid = meta_uitgebreid
            melding.onderwerp = signaal.onderwerp
            melding.save()
            status_instance.melding = melding
            status_instance.save()
            melding.status = status_instance
            melding.save()

            if melding_context:
                melding_context.veld_waardes_toevoegen(meta_uitgebreid)
                melding_context.save()

            melding_gebeurtenis = MeldingGebeurtenis(
                **dict(
                    melding=melding,
                    status=status_instance,
                    omschrijving="Melding aangemaakt",
                )
            )
            melding_gebeurtenis.save()

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
            transaction.on_commit(
                lambda: aangemaakt.send_robust(
                    sender=self.__class__,
                    melding=melding,
                    status=status_instance,
                )
            )

        return melding

    def status_aanpassen(self, data, melding, db="default"):
        from apps.mor.models import Melding, MeldingGebeurtenis
        from apps.status.models import Status

        nieuwe_status_naam = data.get("status", {}).get("naam")

        if melding.status and not melding.status.status_verandering_toegestaan(
            nieuwe_status_naam
        ):
            raise Status.StatusVeranderingNietToegestaan

        with transaction.atomic():
            try:
                locked_melding = (
                    Melding.objects.using(db)
                    .select_for_update(nowait=True)
                    .get(pk=melding.pk)
                )
            except OperationalError:
                raise MeldingManager.MeldingInGebruik

            if melding.status and not melding.status.status_verandering_toegestaan(
                nieuwe_status_naam
            ):
                raise Status.StatusVeranderingNietToegestaan

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
                lambda: status_aangepast.send_robust(
                    sender=self.__class__,
                    melding=locked_melding,
                    status=status_instance,
                    vorige_status=vorige_status,
                )
            )
