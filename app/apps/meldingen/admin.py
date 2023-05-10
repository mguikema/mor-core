from apps.meldingen.models import (
    Bijlage,
    Bron,
    Melder,
    Melding,
    MeldingContext,
    MeldingGebeurtenis,
    MeldingGebeurtenisType,
    Signaal,
    TaakApplicatie,
)
from django.contrib import admin


class SignaalAdmin(admin.ModelAdmin):
    list_display = ("id", "aangemaakt_op", "melding")


class MeldingContextAdmin(admin.ModelAdmin):
    list_display = ("id", "naam", "slug", "aangepast_op")


class MeldingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status_naam",
        "onderwerp_naam",
        "aangemaakt_op",
        "afgesloten_op",
    )

    def status_naam(self, obj):
        try:
            return obj.status.naam
        except Exception:
            return "- leeg -"

    def onderwerp_naam(self, obj):
        try:
            return ", ".join(
                list(obj.onderwerpen.values_list("response_json__naam", flat=True))
            )
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
admin.site.register(MeldingContext, MeldingContextAdmin)
# admin.site.register(Bron, DefaultAdmin)
