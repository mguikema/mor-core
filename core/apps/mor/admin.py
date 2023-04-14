from apps.mor.models import (
    Bijlage,
    Bron,
    Melder,
    Melding,
    MeldingGebeurtenis,
    MeldingGebeurtenisType,
    Signaal,
    TaakApplicatie,
)
from django.contrib import admin


class SignaalAdmin(admin.ModelAdmin):
    list_display = ("id", "aangemaakt_op", "melding")


class MeldingAdmin(admin.ModelAdmin):
    list_display = ("id", "status_naam", "aangemaakt_op", "aangepast_op")

    def status_naam(self, obj):
        try:
            return obj.status.naam
        except Exception:
            return "- leeg -"


class DefaultAdmin(admin.ModelAdmin):
    pass


# admin.site.register(TaakApplicatie, DefaultAdmin)
# admin.site.register(MeldingGebeurtenisType, DefaultAdmin)
admin.site.register(MeldingGebeurtenis, DefaultAdmin)
admin.site.register(Melding, MeldingAdmin)
admin.site.register(Signaal, SignaalAdmin)
admin.site.register(Bijlage, DefaultAdmin)
admin.site.register(Melder, DefaultAdmin)
# admin.site.register(Bron, DefaultAdmin)
