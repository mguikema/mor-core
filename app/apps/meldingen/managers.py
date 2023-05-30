import copy
import logging
from urllib.parse import urlparse

from apps.applicaties.models import Taakapplicatie
from django.contrib.gis.db import models
from django.db import OperationalError, transaction
from django.dispatch import Signal as DjangoSignal
from django.utils import timezone

logger = logging.getLogger(__name__)

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
        from apps.meldingen.models import Melding, MeldingGebeurtenis
        from apps.status.models import Status

        if signaal.melding:
            return signaal.melding

        gevalideerde_onderwerpen = []
        for onderwerp in signaal.onderwerpen:
            try:
                (
                    onderwerp_alias,
                    onderwerp_alias_aangemaakt,
                ) = OnderwerpAlias.objects.get_or_create(bron_url=onderwerp)
                gevalideerde_onderwerpen.append(onderwerp_alias)
                logger.debug(f"{onderwerp_alias}: {onderwerp_alias_aangemaakt}")
            except Exception as e:
                logger.info(f"{onderwerp} werd niet gevonden: {e}")

        if not gevalideerde_onderwerpen:
            raise MeldingManager.OnderwerpenNietValide

        with transaction.atomic():
            data = copy.deepcopy(signaal.ruwe_informatie)
            meta_uitgebreid = data.pop("labels", {})
            melding = Melding()
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

    def taakopdracht_aanmaken(self, serializer, melding, request, db="default"):
        from apps.meldingen.models import Melding
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
            url_o = urlparse(taak_data.get("taaktype", ""))
            taakapplicatie = Taakapplicatie.objects.filter(
                basis_url=f"{url_o.scheme}://{url_o.netloc}"
            ).first()

            taakopdracht = serializer.save(
                taakapplicatie=taakapplicatie,
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
            taak_aanmaken_response = taakapplicatie.taak_aanmaken(taakapplicatie_data)

            if taak_aanmaken_response.status_code == 201:
                taakopdracht.taak_url = (
                    taak_aanmaken_response.json().get("_links", {}).get("self")
                )
                taakopdracht.save()
            else:
                raise Exception(
                    f"De taak kon niet worden aangemaakt in de taakapplicatie: {taak_aanmaken_response.status_code}"
                )

            locked_melding.save()
            transaction.on_commit(
                lambda: taakopdracht_aanmaken.send_robust(
                    sender=self.__class__,
                    taakopdracht=taakopdracht,
                    melding=locked_melding,
                )
            )

        return taakopdracht
