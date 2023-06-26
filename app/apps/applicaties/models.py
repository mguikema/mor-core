import logging
from urllib.parse import urlparse

import requests
from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.core.cache import cache
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
    applicatie_gebruiker_naam = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )
    applicatie_gebruiker_wachtwoord = models.CharField(
        max_length=255,
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

    class AntwoordFout(Exception):
        ...

    @classmethod
    def vind_applicatie_obv_uri(cls, uri):
        url_o = urlparse(uri)
        applicatie = Applicatie.objects.filter(
            basis_url=f"{url_o.scheme}://{url_o.netloc}"
        ).first()
        if not applicatie:
            raise cls.ApplicatieWerdNietGevondenFout(f"uri: {uri}")
        return applicatie

    def encrypt_applicatie_gebruiker_wachtwoord(self, wachtwoord_decrypted):
        f = Fernet(settings.FERNET_KEY)
        self.applicatie_gebruiker_wachtwoord = f.encrypt(
            wachtwoord_decrypted.encode()
        ).decode()

    def haal_taaktypes(self):
        if self.basis_url:
            taaktypes_response = self.taaktypes_halen()
            if taaktypes_response.status_code != 200:
                logger.info(
                    f"url: {self.basis_url}, taaktypes voor applicatie {self.naam} konden niet worden opgehaald: {taaktypes_response.status_code}"
                )
            else:
                self.taaktypes = taaktypes_response.json().get("results", [])

    def _get_timeout(self):
        return (5, 10)

    def get_token_cache_key(self):
        return f"applicatie_{self.uuid}_token"

    def _get_token(self):
        f = Fernet(settings.FERNET_KEY)
        applicatie_token = cache.get(self.get_token_cache_key())
        if (
            not applicatie_token
            and self.applicatie_gebruiker_naam
            and self.applicatie_gebruiker_wachtwoord
        ):
            json_data = {
                "username": self.applicatie_gebruiker_naam,
                "password": f.decrypt(self.applicatie_gebruiker_wachtwoord).decode(),
            }
            try:
                token_response = requests.post(
                    f"{self.basis_url}{settings.TOKEN_API_RELATIVE_URL}",
                    json=json_data,
                )
            except Exception:
                return

            if token_response.status_code == 200:
                applicatie_token = token_response.json().get("token")
                cache.set(
                    self.get_token_cache_key(),
                    applicatie_token,
                    settings.MELDINGEN_TOKEN_TIMEOUT,
                )
        return applicatie_token

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
        token = self._get_token()
        if not token:
            return {}
        headers = {"Authorization": f"Token {token}"}
        return headers

    def _do_request(self, url, method="get", data={}, raw_response=True):
        action: Request = getattr(requests, method)
        action_params: dict = {
            "url": self._get_url(url),
            "headers": self._get_headers(),
            "json": data,
            "timeout": self._get_timeout(),
        }
        try:
            response: Response = action(**action_params)
        except Exception as e:
            raise Applicatie.AntwoordFout(f"error: {e}")
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
            try:
                return response.json()
            except Exception:
                raise Applicatie.NotificatieVoorApplicatieFout(
                    f"url: '{signaal_uri}melding-afgesloten/', response tekst: {response.text}"
                )
        raise Applicatie.NotificatieVoorApplicatieFout(
            f"url: '{signaal_uri}melding-afgesloten/', status code: {response.status_code}"
        )
