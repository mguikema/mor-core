from apps.locatie.models import Adres, Graf, Lichtmast, Locatie
from django.contrib import admin
from django.contrib.gis.db import models
from django.forms.widgets import Textarea


class GrafAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "aangemaakt_op", "begraafplaats")


class LocatieAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "aangemaakt_op",
        "begraafplaats",
        "melding",
        "signaal",
    )

    # TODO: Remove later!!!
    formfield_overrides = {
        models.GeometryField: {"widget": Textarea(attrs={"rows": 2})}
    }


class AdresAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "aangemaakt_op", "melding", "signaal", "straatnaam")


class LichtmastAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "aangemaakt_op", "melding", "signaal", "lichtmast_id")


admin.site.register(Graf, GrafAdmin)
admin.site.register(Adres, AdresAdmin)
admin.site.register(Lichtmast, LichtmastAdmin)
admin.site.register(Locatie, LocatieAdmin)
