import copy

from django.contrib.gis.db import models
from django.contrib.sites.models import Site
from django.db import OperationalError, transaction
from django.dispatch import Signal as DjangoSignal
from django.urls import reverse
from django.utils import timezone

aangemaakt = DjangoSignal()
status_aangepast = DjangoSignal()
gebeurtenis_toegevoegd = DjangoSignal()
taakopdracht_aanmaken = DjangoSignal()


class MeldingManager(models.Manager):
    class OnderwerpenNietValide(Exception):
        pass

    class StatusVeranderingNietToegestaan(Exception):
        pass

    class MeldingContextInGebruik(Exception):
        pass

    class MeldingInGebruik(Exception):
        pass

    class MeldingContextOnderwerpNietGevonden(Exception):
        pass

    def aanmaken(self, signaal, db="default"):
        from apps.aliassen.models import OnderwerpAlias
        from apps.locatie.models import Graf
        from apps.meldingen.models import Melding, MeldingContext, MeldingGebeurtenis
        from apps.status.models import Status

        if signaal.melding:
            return signaal.melding

        gevalideerde_onderwerpen = OnderwerpAlias.objects.filter(
            bron_url__in=signaal.onderwerpen
        )
        if not gevalideerde_onderwerpen:
            raise MeldingManager.OnderwerpenNietValide

        with transaction.atomic():
            try:
                melding_context = (
                    MeldingContext.objects.using(db)
                    .select_for_update(nowait=True)
                    .filter(onderwerpen__in=gevalideerde_onderwerpen)
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
            melding.save()
            melding.onderwerpen.set(gevalideerde_onderwerpen)
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
                    gebeurtenis_type=MeldingGebeurtenis.GebeurtenisType.MELDING_AANGEMAAKT,
                    status=status_instance,
                    omschrijving_intern="Melding aangemaakt",
                )
            )
            melding_gebeurtenis.save()
            Graf.objects.create(
                **{
                    "melding": melding,
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

    def status_aanpassen(self, serializer, melding, db="default"):
        from apps.meldingen.models import Melding

        with transaction.atomic():
            try:
                locked_melding = (
                    Melding.objects.using(db)
                    .select_for_update(nowait=True)
                    .get(pk=melding.pk)
                )
            except OperationalError:
                raise MeldingManager.MeldingInGebruik

            vorige_status = locked_melding.status

            resolutie = serializer.validated_data.pop("resolutie", None)
            melding_gebeurtenis = serializer.save()

            locked_melding.status = melding_gebeurtenis.status

            if not locked_melding.status.volgende_statussen():
                locked_melding.afgesloten_op = timezone.now().isoformat()
                if resolutie in [ro[0] for ro in Melding.ResolutieOpties.choices]:
                    locked_melding.resolutie = resolutie
            locked_melding.save()
            transaction.on_commit(
                lambda: status_aangepast.send_robust(
                    sender=self.__class__,
                    melding=locked_melding,
                    status=melding_gebeurtenis.status,
                    vorige_status=vorige_status,
                )
            )

    def gebeurtenis_toevoegen(self, serializer, melding, db="default"):
        from apps.meldingen.models import Melding

        with transaction.atomic():
            try:
                locked_melding = (
                    Melding.objects.using(db)
                    .select_for_update(nowait=True)
                    .get(pk=melding.pk)
                )
            except OperationalError:
                raise MeldingManager.MeldingInGebruik

            serializer.save()

            locked_melding.save()
            transaction.on_commit(
                lambda: gebeurtenis_toegevoegd.send_robust(
                    sender=self.__class__,
                    melding=locked_melding,
                )
            )

    def taakopdracht_aanmaken(self, serializer, melding, db="default"):
        from apps.meldingen.models import Melding
        from apps.taken.models import Taakgebeurtenis, Taakstatus
        from apps.taken.serializers import TaakSerializerExtern

        with transaction.atomic():
            try:
                locked_melding = (
                    Melding.objects.using(db)
                    .select_for_update(nowait=True)
                    .get(pk=melding.pk)
                )
            except OperationalError:
                raise MeldingManager.MeldingInGebruik

            taak_data = {}
            taak_data.update(serializer.validated_data)
            taak_data.update(
                {
                    "melding": f'{Site.objects.get_current().domain}{reverse("app:melding-detail", kwargs={"uuid": melding.uuid})}',
                }
            )

            taak_serializer_extern = TaakSerializerExtern(data=taak_data)
            taakopdracht = None
            if taak_serializer_extern.is_valid():
                taak_aanmaken_response = serializer.validated_data.get(
                    "taakapplicatie"
                ).taak_aanmaken(taak_serializer_extern.validated_data)
                if taak_aanmaken_response.status_code == 201:
                    taakopdracht = serializer.save()
                    taakopdracht.taak_url = taak_aanmaken_response.json().get("link")
                    taakstatus_instance = Taakstatus()
                    taakstatus_instance.save()
                    taakgebeurtenis_instance = Taakgebeurtenis(
                        taakopdracht=taakopdracht,
                        taakstatus=taakstatus_instance,
                        omschrijving_intern="Taak aangemaakt",
                    )
                    taakopdracht.status = taakstatus_instance
                    taakopdracht.save()
                    taakgebeurtenis_instance.save()

                    locked_melding.save()

            transaction.on_commit(
                lambda: taakopdracht_aanmaken.send_robust(
                    sender=self.__class__,
                    taakopdracht=taakopdracht,
                    melding=locked_melding,
                )
            )
