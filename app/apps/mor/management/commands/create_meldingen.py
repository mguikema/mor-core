"""
Management utility to create superusers.
"""

import requests
from django.core.management.base import BaseCommand


class NotRunningInTTYException(Exception):
    pass


PASSWORD_FIELD = "password"


class Command(BaseCommand):
    def handle(self, *args, **options):
        b64_file = "e1xydGYxXGFuc2lcYW5zaWNwZzEyNTJcY29jb2FydGYyNTgwClxjb2NvYXRleHRzY2FsaW5nMFxjb2NvYXBsYXRmb3JtMHtcZm9udHRibFxmMFxmc3dpc3NcZmNoYXJzZXQwIEhlbHZldGljYTt9CntcY29sb3J0Ymw7XHJlZDI1NVxncmVlbjI1NVxibHVlMjU1O30Ke1wqXGV4cGFuZGVkY29sb3J0Ymw7O30KXHBhcGVydzExOTAwXHBhcGVyaDE2ODQwXG1hcmdsMTQ0MFxtYXJncjE0NDBcdmlld3cxMTUyMFx2aWV3aDg0MDBcdmlld2tpbmQwClxwYXJkXHR4NTY2XHR4MTEzM1x0eDE3MDBcdHgyMjY3XHR4MjgzNFx0eDM0MDFcdHgzOTY4XHR4NDUzNVx0eDUxMDJcdHg1NjY5XHR4NjIzNlx0eDY4MDNccGFyZGlybmF0dXJhbFxwYXJ0aWdodGVuZmFjdG9yMAoKXGYwXGZzMjQgXGNmMCBUZXN0IGZpbGV9Cg=="

        data = {
            "melder": {
                "voornaam": "string",
                "achternaam": "string",
                "email": "user@example.com",
                "telefoonnummer": "string",
            },
            "bijlagen": [
                {
                    "bestand": b64_file,
                }
            ],
            "origineel_aangemaakt": "2023-03-09T11:56:04.036Z",
            "tekst": "string",
            "ruwe_informatie": {
                "vak": "kuhi",
                "labels": {
                    "vak": {"label": "Vak", "choices": None},
                    "fotos": {"label": "Foto's", "choices": None},
                    "aannemer": {
                        "label": "Wie heeft het verzoek aangenomen?",
                        "choices": {
                            "": "Selecteer een medewerker",
                            "onbekend": "Onbekend",
                        },
                    },
                    "no_email": {
                        "label": "De melder beschikt niet over een e-mailadres.",
                        "choices": None,
                    },
                    "categorie": {
                        "label": "Categorie",
                        "choices": {
                            "1": "Verzakking eigen graf",
                            "2": "Verzakking algemeen",
                            "3": "Snoeien",
                            "4": "Beplanting",
                            "5": "Schoonmaken",
                            "6": "Verdwenen materiaal",
                            "7": "Gaten",
                            "8": "Wespennest",
                            "9": "Konijnen",
                            "10": "Muizen",
                            "11": "Zerk reinigen",
                            "12": "Overig",
                        },
                    },
                    "grafnummer": {"label": "Grafnummer", "choices": None},
                    "naam_melder": {"label": "Naam", "choices": None},
                    "toelichting": {"label": "Toelichting", "choices": None},
                    "email_melder": {"label": "E-mailadres", "choices": None},
                    "begraafplaats": {
                        "label": "Begraafplaats",
                        "choices": {
                            "": "Selecteer een begraafplaats",
                            "1": "Begraafplaats Crooswijk",
                            "2": "Begraafplaats Hoek van Holland",
                            "3": "Begraafplaats en crematorium Hofwijk",
                            "4": "Begraafplaats Oudeland, Hoogvliet",
                            "5": "Begraafplaats Oud-Hoogvliet",
                            "6": "Begraafplaats Oud-Overschie",
                            "7": "Begraafplaats Oud-Pernis",
                            "8": "Begraafplaats Oud-Schiebroek",
                            "9": "Begraafplaats Pernis",
                            "10": "Begraafplaats Rozenburg",
                            "11": "Zuiderbegraafplaats",
                        },
                    },
                    "rechthebbende": {
                        "label": "Is deze persoon de rechthebbende of belanghebbende?",
                        "choices": {"0": "Nee", "1": "Ja", "2": "Onbekend"},
                    },
                    "specifiek_graf": {
                        "label": "Betreft het verzoek een specifiek graf?",
                        "choices": {"0": "Nee", "1": "Ja"},
                    },
                    "naam_overledene": {"label": "Naam overledene", "choices": None},
                    "telefoon_melder": {"label": "Telefoonnummer", "choices": None},
                    "terugkoppeling_gewenst2": {
                        "label": "Is terugkoppeling gewenst?",
                        "choices": {"0": "Nee", "11": "Ja"},
                    },
                },
                "aannemer": "onbekend",
                "no_email": False,
                "categorie": ["1", "4"],
                "grafnummer": "jhgnjk",
                "naam_melder": "mliuyi",
                "toelichting": "lmiuyi",
                "email_melder": "m@m.nl",
                "begraafplaats": "2",
                "rechthebbende": "0",
                "specifiek_graf": "1",
                "naam_overledene": "mkh",
                "telefoon_melder": "kuhiuo",
                "terugkoppeling_gewenst2": "0",
            },
            "bron": "mock_bron",
            "onderwerpen": [
                "http://mor-core.forzamor.local:8002/v1/onderwerp/verzakking-eigen-graf/"
            ],
            "graven": [
                {
                    "bron": "string",
                    "plaatsnaam": "string",
                    "begraafplaats": "7",
                    "grafnummer": "string",
                    "vak": "string",
                    "geometrieen": [],
                }
            ],
        }
        headers = {"Authorization": "Token de54d4cd5de6e87748bf51560a9345ee42a0076a"}
        for i in range(0, 1000):
            response = requests.post(
                "http://host.docker.internal:8002/v1/signaal/",
                json=data,
                headers=headers,
            )
            print(response.status_code)
