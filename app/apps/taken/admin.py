from apps.taken.models import Taakgebeurtenis, Taakopdracht
from django.contrib import admin


class TaakgebeurtenisAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "taakstatus",
        "aangemaakt_op",
        "aangepast_op",
        "taakopdracht",
        "gebruiker",
    )


class TaakopdrachtAdmin(admin.ModelAdmin):
    list_editable = ("taaktype", "taak_url")
    list_display = (
        "id",
        "taaktype",
        "taak_url",
        # "uuid",
        "titel",
        # "aangemaakt_op",
        # "aangepast_op",
        # "melding",
        "status",
        "resolutie",
    )


admin.site.register(Taakopdracht, TaakopdrachtAdmin)
admin.site.register(Taakgebeurtenis, TaakgebeurtenisAdmin)
