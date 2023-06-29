from apps.authenticatie.managers import GebruikerManager
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models


class Gebruiker(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = GebruikerManager()

    def __str__(self):
        return self.email
