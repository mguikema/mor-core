import logging

from apps.applicaties.models import Applicatie
from django.contrib.gis.db import models
from django.db import OperationalError, transaction
from django.dispatch import Signal as DjangoSignal
from django.utils import timezone
from rest_framework.reverse import reverse

logger = logging.getLogger(__name__)

aangemaakt = DjangoSignal()
status_aangepast = DjangoSignal()
afgesloten = DjangoSignal()
gebeurtenis_toegevoegd = DjangoSignal()
taakopdracht_aangemaakt = DjangoSignal()
taakopdracht_status_aangepast = DjangoSignal()


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

    def aanmaken(self, signaal_validated_data, signaal_initial_data, db="default"):
        from apps.meldingen.models import MeldingGebeurtenis, Signaal
        from apps.meldingen.serializers import MeldingAanmakenSerializer
        from apps.status.models import Status

        with transaction.atomic():

            gevalideerde_onderwerpen = []
            for onderwerp in signaal_validated_data.get("onderwerpen", []):
                gevalideerde_onderwerpen.append(
                    {
                        "bron_url": onderwerp,
                    }
                )
            if not gevalideerde_onderwerpen:
                raise MeldingManager.OnderwerpenNietValide

            melding_data = {}
            melding_data.update(signaal_initial_data)
            signaal_initial_data.pop("bijlagen", None)

            melding_data["onderwerpen"] = gevalideerde_onderwerpen
            melding_serializer = MeldingAanmakenSerializer(data=melding_data)
            if melding_serializer.is_valid():
                melding = melding_serializer.save()
            else:
                raise Exception(melding_serializer.errors)

            status_instance = Status()
            status_instance.melding = melding
            status_instance.save()
            melding.status = status_instance
            melding.save()

            melding_gebeurtenis = MeldingGebeurtenis(
                melding=melding,
                gebeurtenis_type=MeldingGebeurtenis.GebeurtenisType.MELDING_AANGEMAAKT,
                status=status_instance,
                omschrijving_intern="Melding aangemaakt",
            )
            melding_gebeurtenis.save()

            signaal = Signaal.objects.create(
                signaal_url=signaal_initial_data.get("signaal_url"),
                signaal_data=signaal_initial_data,
                melding=melding,
            )

            transaction.on_commit(
                lambda: aangemaakt.send_robust(
                    sender=self.__class__,
                    melding=melding,
                    status=status_instance,
                )
            )
        return signaal

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

            meldinggebeurtenis = serializer.save(
                melding=melding,
            )

            locked_melding.save()
            transaction.on_commit(
                lambda: gebeurtenis_toegevoegd.send_robust(
                    sender=self.__class__,
                    melding=locked_melding,
                    meldinggebeurtenis=meldinggebeurtenis,
                )
            )

    def taakopdracht_aanmaken(self, serializer, melding, request, db="default"):
        from apps.meldingen.models import Melding, MeldingGebeurtenis
        from apps.status.models import Status
        from apps.taken.models import Taakgebeurtenis, Taakstatus

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
            applicatie = Applicatie.vind_applicatie_obv_uri(
                taak_data.get("taaktype", "")
            )

            if not applicatie:
                raise Exception(
                    f"De applicatie kon niet worden geonden op basis van dit taaktype: {taak_data.get('taaktype', '')}"
                )
            taakopdracht = serializer.save(
                applicatie=applicatie,
                melding=melding,
            )
            taakstatus_instance = Taakstatus(
                taakopdracht=taakopdracht,
            )
            taakstatus_instance.save()

            taakopdracht.status = taakstatus_instance
            taakopdracht.save()

            taakgebeurtenis_instance = Taakgebeurtenis(
                taakopdracht=taakopdracht,
                taakstatus=taakstatus_instance,
                omschrijving_intern="Taak aangemaakt",
            )
            taakgebeurtenis_instance.save()

            taakapplicatie_data = serializer.__class__(
                taakopdracht, context={"request": request}
            ).data
            taakapplicatie_data["melding"] = taakapplicatie_data.get("_links", {}).get(
                "melding"
            )
            taakapplicatie_data["taakopdracht"] = reverse(
                "v1:taakopdracht-detail",
                kwargs={"uuid": taakopdracht.uuid},
                request=request,
            )
            taak_aanmaken_response = applicatie.taak_aanmaken(taakapplicatie_data)

            if taak_aanmaken_response.status_code == 201:
                taakopdracht.taak_url = (
                    taak_aanmaken_response.json().get("_links", {}).get("self")
                )
                taakopdracht.save()
            else:
                raise Exception(
                    f"De taak kon niet worden aangemaakt in de applicatie: {taak_aanmaken_response.status_code}"
                )

            melding_gebeurtenis = MeldingGebeurtenis(
                melding=locked_melding,
                gebeurtenis_type=MeldingGebeurtenis.GebeurtenisType.TAAKOPDRACHT_AANGEMAAKT,
                taakopdracht=taakopdracht,
                taakgebeurtenis=taakgebeurtenis_instance,
            )

            # zet status van de melding naar in_behandeling als dit niet de huidige status is
            if locked_melding.status.naam != Status.NaamOpties.IN_BEHANDELING:
                status_instance = Status(naam=Status.NaamOpties.IN_BEHANDELING)
                status_instance.melding = locked_melding
                status_instance.save()
                locked_melding.status = status_instance
                melding_gebeurtenis.status = status_instance
                melding_gebeurtenis.gebeurtenis_type = (
                    MeldingGebeurtenis.GebeurtenisType.STATUS_WIJZIGING
                )

            melding_gebeurtenis.save()
            locked_melding.save()
            transaction.on_commit(
                lambda: taakopdracht_aangemaakt.send_robust(
                    sender=self.__class__,
                    taakopdracht=taakopdracht,
                    melding=locked_melding,
                )
            )

        return taakopdracht

    def taakopdracht_status_aanpassen(
        self, serializer, taakopdracht, request, db="default"
    ):
        from apps.meldingen.models import Melding, MeldingGebeurtenis
        from apps.status.models import Status
        from apps.taken.models import Taakopdracht

        with transaction.atomic():
            try:
                locked_melding = (
                    Melding.objects.using(db)
                    .select_for_update(nowait=True)
                    .get(pk=taakopdracht.melding.pk)
                )
                locked_taakopdracht = (
                    Taakopdracht.objects.using(db)
                    .select_for_update(nowait=True)
                    .get(pk=taakopdracht.pk)
                )
            except OperationalError:
                raise MeldingManager.MeldingInGebruik

            resolutie = serializer.validated_data.pop("resolutie", None)
            taakgebeurtenis = serializer.save(
                taakopdracht=locked_taakopdracht,
            )

            locked_taakopdracht.status = taakgebeurtenis.taakstatus

            if not locked_taakopdracht.status.volgende_statussen():
                locked_taakopdracht.afgesloten_op = timezone.now().isoformat()
                if resolutie in [ro[0] for ro in Taakopdracht.ResolutieOpties.choices]:
                    locked_taakopdracht.resolutie = resolutie

            taak_status_aanpassen_data = {
                "taakstatus": {"naam": taakgebeurtenis.taakstatus.naam},
                "bijlagen": [
                    reverse(
                        "v1:bijlage-detail",
                        kwargs={"uuid": bijlage.uuid},
                        request=request,
                    )
                    for bijlage in taakgebeurtenis.bijlagen.all()
                ],
                "resolutie": resolutie,
                "omschrijving_intern": taakgebeurtenis.omschrijving_intern,
            }
            taak_status_aanpassen_response = (
                locked_taakopdracht.applicatie.taak_status_aanpassen(
                    f"{locked_taakopdracht.taak_url}status-aanpassen/",
                    data=taak_status_aanpassen_data,
                )
            )

            if taak_status_aanpassen_response.status_code != 200:
                raise Exception(
                    f"De taakstatus kon niet worden aangepast: {locked_taakopdracht.taak_url}status-aanpassen/"
                )

            melding_gebeurtenis = MeldingGebeurtenis(
                melding=locked_melding,
                gebeurtenis_type=MeldingGebeurtenis.GebeurtenisType.TAAKOPDRACHT_STATUS_WIJZIGING,
                taakopdracht=locked_taakopdracht,
                taakgebeurtenis=taakgebeurtenis,
            )

            # zet status van de melding naar in_behandeling als dit niet de huidige status is
            locked_taakopdracht.save()

            if not locked_melding.actieve_taakopdrachten():
                status_instance = Status(naam=Status.NaamOpties.CONTROLE)
                status_instance.melding = locked_melding
                status_instance.save()
                locked_melding.status = status_instance
                melding_gebeurtenis.status = status_instance
                melding_gebeurtenis.gebeurtenis_type = (
                    MeldingGebeurtenis.GebeurtenisType.STATUS_WIJZIGING
                )

            melding_gebeurtenis.save()

            locked_melding.save()
            transaction.on_commit(
                lambda: taakopdracht_status_aangepast.send_robust(
                    sender=self.__class__,
                    melding=locked_melding,
                    taakopdracht=locked_taakopdracht,
                    taakgebeurtenis=taakgebeurtenis,
                )
            )

        return taakopdracht
