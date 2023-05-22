from apps.taken.models import Taakopdracht
from django.contrib import admin


class TaakopdrachtAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "titel",
        "aangemaakt_op",
        "aangepast_op",
        "melding",
    )


admin.site.register(Taakopdracht, TaakopdrachtAdmin)
