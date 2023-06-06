from apps.locatie.models import Adres, Graf, Lichtmast, Locatie
from django.contrib import admin


class GrafAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "aangemaakt_op", "begraafplaats")


class LocatieAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "aangemaakt_op", "begraafplaats", "melding")


class AdresAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "aangemaakt_op", "melding", "straatnaam")


class LichtmastAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "aangemaakt_op", "melding", "lichtmast_id")


admin.site.register(Graf, GrafAdmin)
admin.site.register(Adres, AdresAdmin)
admin.site.register(Lichtmast, LichtmastAdmin)
admin.site.register(Locatie, LocatieAdmin)
