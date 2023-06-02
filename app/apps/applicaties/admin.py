from apps.applicaties.models import Applicatie
from django.contrib import admin


class TaakapplicatieAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "naam",
        "gebruiker",
        "melding_context",
    )


admin.site.register(Applicatie, TaakapplicatieAdmin)
