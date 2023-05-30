import logging

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
        taaktypes_response = self.taaktypes_halen()
        if taaktypes_response.status_code != 200:
            logger.info(
                f"taaktypes voor taakapplicatie {self.naam} konden niet worden gahaalt: {taaktypes_response.status_code}"
            )
        self.taaktypes = self.taaktypes_halen().json().get("results", [])

    class ApplicationAuthResponseException(Exception):
        pass

    def _get_timeout(self):
        return (5, 10)

    def _get_token(self):
        return self.gebruiker.auth_token.key

    def _get_url(self, url):
        return f"{self.basis_url}{url}"

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
        return self._do_request("/v1/taak/", method="post", data=data)

    def taaktypes_halen(self):
        return self._do_request("/v1/taaktype/", method="get")
