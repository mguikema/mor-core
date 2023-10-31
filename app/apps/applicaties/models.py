import logging
from urllib.parse import urlencode, urlparse

import requests
from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.core.cache import cache
from requests import Request, Response
from utils.models import BasisModel

logger = logging.getLogger(__name__)


def encrypt_gebruiker_wachtwoord(wachtwoord_decrypted):
    f = Fernet(settings.FERNET_KEY)
    wachtwoord_encrypted = f.encrypt(wachtwoord_decrypted.encode()).decode()
    return wachtwoord_encrypted


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

    def __str__(self):
        return self.naam

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
        self.applicatie_gebruiker_wachtwoord = encrypt_gebruiker_wachtwoord(
            wachtwoord_decrypted
        )

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

    def _do_request(
        self, url, method="get", data={}, params={}, raw_response=True, cache_timeout=0
    ):
        action: Request = getattr(requests, method)
        url = self._get_url(url)
        action_params: dict = {
            "url": url,
            "headers": self._get_headers(),
            "json": data,
            "params": params,
            "timeout": self._get_timeout(),
        }
        if cache_timeout and method == "get":
            cache_key = f"{url}?{urlencode(params)}"
            response = cache.get(cache_key)
            if not response:
                try:
                    response: Response = action(**action_params)
                except Exception as e:
                    raise Applicatie.AntwoordFout(f"error: {e}")
                if int(response.status_code) == 200:
                    cache.set(cache_key, response, cache_timeout)
        else:
            try:
                response: Response = action(**action_params)
            except Exception as e:
                raise Applicatie.AntwoordFout(f"error: {e}")
        if raw_response:
            return response
        return response.json()

    def taak_aanmaken(self, data):
        return self._do_request("/api/v1/taak/", method="post", data=data)

    def taak_verwijderen(self, url):
        return self._do_request(url, method="delete")

    def taaktypes_halen(self):
        if self.basis_url:
            taaktypes_response = self._do_request(
                "/api/v1/taaktype/",
                params={"limit": 100},
                method="get",
                cache_timeout=60,
            )
            if taaktypes_response.status_code == 404:
                logger.error(
                    f"url: {self.basis_url}, taaktypes voor applicatie '{self.naam}' konden niet worden opgehaald: status_code={taaktypes_response.status_code}"
                )
                return []
            if taaktypes_response.status_code != 200:
                logger.error(
                    f"url: {self.basis_url}, taaktypes voor applicatie '{self.naam}' konden niet worden opgehaald: status_code={taaktypes_response.status_code}, text={taaktypes_response.text}"
                )
                return []
            return taaktypes_response.json().get("results", [])
        else:
            logger.info(
                f"taaktypes voor applicatie '{self.naam}' konden niet worden opgehaald: basis_url ontbreekt"
            )
        return []

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
