from apps.locatie.models import Adres, Geometrie, Graf, Locatie
from django.contrib import admin


class GrafAdmin(admin.ModelAdmin):
    list_display = ("id", "begraafplaats")


class LocatieAdmin(admin.ModelAdmin):
    list_display = ("id", "begraafplaats", "melding")


class DefaultAdmin(admin.ModelAdmin):
    ...


admin.site.register(Graf, GrafAdmin)
admin.site.register(Adres, DefaultAdmin)
admin.site.register(Locatie, LocatieAdmin)
admin.site.register(Geometrie, DefaultAdmin)
