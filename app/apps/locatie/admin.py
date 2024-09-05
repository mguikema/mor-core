from apps.locatie.models import Adres, Graf, Lichtmast, Locatie
from apps.locatie.tasks import update_locatie_zoek_field_task
from django.contrib import admin, messages
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
        "wijknaam",
        "gewicht",
        "signaal",
        "huisnummer",
        "straatnaam",
        "geometrie",
    )

    # TODO: Remove later!!!
    formfield_overrides = {
        models.GeometryField: {"widget": Textarea(attrs={"rows": 2})}
    }
    raw_id_fields = (
        "melding",
        "signaal",
        "gebruiker",
    )
    actions = ["update_locatie_zoek_field"]

    @admin.action(description="Update locatie_zoek_field for selected locations")
    def update_locatie_zoek_field(self, request, queryset):
        result = update_locatie_zoek_field_task.delay()
        self.message_user(
            request,
            f"Task to update locatie_zoek_field has been queued. Task ID: {result.id}",
            messages.SUCCESS,
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "melding",
            "signaal",
        )


class AdresAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "aangemaakt_op", "melding", "signaal", "straatnaam")


class LichtmastAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "aangemaakt_op", "melding", "signaal", "lichtmast_id")


admin.site.register(Graf, GrafAdmin)
admin.site.register(Adres, AdresAdmin)
admin.site.register(Lichtmast, LichtmastAdmin)
admin.site.register(Locatie, LocatieAdmin)
