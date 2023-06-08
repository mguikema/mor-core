import logging
from urllib.parse import urlparse

import requests
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from requests import Request, Response
from utils.models import BasisModel

logger = logging.getLogger(__name__)


class Taakapplicatie(BasisModel):
    """
    Representeerd externe applicaite die de afhandling van de melden op zich nemen.
    """

    naam = models.CharField(
        max_length=100,
        default="Taakapplicatie",
    )
    basis_url = models.URLField(
        blank=True,
        null=True,
    )
    gebruiker = models.ForeignKey(
        to=get_user_model(),
        related_name="taakapplicatie_voor_gebruiker",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    onderwerpen = models.ManyToManyField(
        to="aliassen.OnderwerpAlias",
        related_name="taakapplicaties_voor_onderwerpen",
        blank=True,
    )
    taaktypes = models.JSONField(
        default=list,
        blank=True,
        null=True,
    )
    melding_context = models.ForeignKey(
        to="meldingen.MeldingContext",
        related_name="taakapplicatie_voor_melding_context",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def haal_taaktypes(self):
        if self.basis_url:
            taaktypes_response = self.taaktypes_halen()
            if taaktypes_response.status_code != 200:
                logger.info(
                    f"taaktypes voor applicatie {self.naam} konden niet worden gahaalt: {taaktypes_response.status_code}"
                )
            self.taaktypes = self.taaktypes_halen().json().get("results", [])

    class ApplicationAuthResponseException(Exception):
        ...

    class ApplicatieBasisUrlFout(Exception):
        ...

    def _get_timeout(self):
        return (5, 10)

    def _get_token(self):
        # TODO haal token van applicatie token endpoint
        return "token"

    def _get_url(self, url):
        url_o = urlparse(url)
        if not url_o.scheme and not url_o.netloc:
            return f"{self.basis_url}{url}"
        if f"{url_o.scheme}://{url_o.netloc}" == self.basis_url:
            return url
        raise Applicatie.ApplicatieBasisUrlFout(
            f"url: {url}, basis_url: {self.basis_url}"
        )

    def _get_headers(self):
        headers = {"Authorization": f"Token {self._get_token()}"}
        return headers

    def _do_request(self, url, method="get", data={}, raw_response=True):
        action: Request = getattr(requests, method)
        action_params: dict = {
            "url": self._get_url(url),
            "headers": self._get_headers(),
            "json": data,
            "timeout": self._get_timeout(),
        }
        response: Response = action(**action_params)
        if raw_response:
            return response
        return response.json()

    def taak_aanmaken(self, data):
        return self._do_request("/api/v1/taak/", method="post", data=data)

    def taaktypes_halen(self):
        return self._do_request("/api/v1/taaktype/", method="get")

    def taak_status_aanpassen(self, url, data):
        return self._do_request(url, method="patch", data=data)


class Applicatie(BasisModel):
    """
    Representeerd externe applicaite die de afhandling van de melden op zich nemen.
    """

    naam = models.CharField(
        max_length=100,
        default="Applicatie",
    )
    basis_url = models.URLField(
        blank=True,
        null=True,
    )
    gebruiker = models.ForeignKey(
        to=get_user_model(),
        related_name="applicaties_voor_gebruiker",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    onderwerpen = models.ManyToManyField(
        to="aliassen.OnderwerpAlias",
        related_name="applicaties_voor_onderwerpen",
        blank=True,
    )
    taaktypes = models.JSONField(
        default=list,
        blank=True,
        null=True,
    )
    melding_context = models.ForeignKey(
        to="meldingen.MeldingContext",
        related_name="applicatie_voor_melding_context",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    @classmethod
    def vind_applicatie_obv_uri(cls, uri):
        url_o = urlparse(uri)
        applicatie = Applicatie.objects.filter(
            basis_url=f"{url_o.scheme}://{url_o.netloc}"
        ).first()
        if not applicatie:
            raise cls.ApplicatieWerdNietGevondenFout(f"uri: {uri}")
        return applicatie

    def haal_taaktypes(self):
        if self.basis_url:
            taaktypes_response = self.taaktypes_halen()
            if taaktypes_response.status_code != 200:
                logger.info(
                    f"url: {self.basis_url}, taaktypes voor applicatie {self.naam} konden niet worden opgehaald: {taaktypes_response.status_code}"
                )
            else:
                self.taaktypes = taaktypes_response.json().get("results", [])

    class ApplicationAuthResponseException(Exception):
        ...

    class ApplicatieBasisUrlFout(Exception):
        ...

    class ApplicatieWerdNietGevondenFout(Exception):
        ...

    class NotificatieVoorApplicatieFout(Exception):
        ...

    class TaaktypesOphalenFout(Exception):
        ...

    def _get_timeout(self):
        return (5, 10)

    def _get_token(self):
        # TODO haal token van applicatie token endpoint
        return "token"

    def _get_url(self, url):
        url_o = urlparse(url)
        if not url_o.scheme and not url_o.netloc:
            return f"{self.basis_url}{url}"
        if f"{url_o.scheme}://{url_o.netloc}" == self.basis_url:
            return url
        raise Applicatie.ApplicatieBasisUrlFout(
            f"url: {url}, basis_url: {self.basis_url}"
        )

    def _get_headers(self):
        headers = {"Authorization": f"Token {self._get_token()}"}
        return headers

    def _do_request(self, url, method="get", data={}, raw_response=True):
        action: Request = getattr(requests, method)
        action_params: dict = {
            "url": self._get_url(url),
            "headers": self._get_headers(),
            "json": data,
            "timeout": self._get_timeout(),
        }
        response: Response = action(**action_params)
        if raw_response:
            return response
        return response.json()

    def taak_aanmaken(self, data):
        return self._do_request("/api/v1/taak/", method="post", data=data)

    def taaktypes_halen(self):
        return self._do_request("/api/v1/taaktype/", method="get")

    def taak_status_aanpassen(self, url, data):
        return self._do_request(url, method="patch", data=data)

    def notificatie_melding_afgesloten(self, signaal_uri):
        response = self._do_request(f"{signaal_uri}melding-afgesloten/")
        if response.status_code == 200:
            return response.json()
        else:
            raise Applicatie.NotificatieVoorApplicatieFout(
                f"url: '{signaal_uri}melding-afgesloten/', status code: {response.status_code}"
            )
