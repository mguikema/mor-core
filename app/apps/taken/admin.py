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
    )


class TaakopdrachtAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "titel",
        "aangemaakt_op",
        "aangepast_op",
        "melding",
    )


admin.site.register(Taakopdracht, TaakopdrachtAdmin)
admin.site.register(Taakgebeurtenis, TaakgebeurtenisAdmin)
