from apps.meldingen.models import (
    Bijlage,
    Melder,
    Melding,
    MeldingContext,
    MeldingGebeurtenis,
    Signaal,
)
from apps.meldingen.tasks import (
    task_aanmaken_afbeelding_versies,
    task_notificatie_voor_signaal_melding_afgesloten,
)
from django.contrib import admin


@admin.action(description="Maak afbeelding versies voor selectie")
def action_aanmaken_afbeelding_versies(modeladmin, request, queryset):
    for bijlage in queryset.all():
        task_aanmaken_afbeelding_versies.delay(bijlage.id)


class BijlageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "aangemaakt_op",
        "bestand",
        "is_afbeelding",
        "mimetype",
        "content_object",
        "afbeelding",
    )
    actions = (action_aanmaken_afbeelding_versies,)


class SignaalAdmin(admin.ModelAdmin):
    list_display = ("id", "uuid", "aangemaakt_op", "melding")


class MeldingContextAdmin(admin.ModelAdmin):
    list_display = ("id", "naam", "slug", "aangepast_op")


@admin.action(description="Signalen afsluiten voor melding")
def action_notificatie_voor_signaal_melding_afgesloten(modeladmin, request, queryset):
    for melding in queryset.all():
        if melding.afgesloten_op:
            for signaal in melding.signalen_voor_melding.all():
                task_notificatie_voor_signaal_melding_afgesloten.delay(signaal.id)


class MeldingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "status_naam",
        "onderwerp_naam",
        "aangemaakt_op",
        "afgesloten_op",
    )
    actions = (action_notificatie_voor_signaal_melding_afgesloten,)

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


admin.site.register(MeldingGebeurtenis, DefaultAdmin)
admin.site.register(Melding, MeldingAdmin)
admin.site.register(Signaal, SignaalAdmin)
admin.site.register(Bijlage, BijlageAdmin)
admin.site.register(Melder, DefaultAdmin)
admin.site.register(MeldingContext, MeldingContextAdmin)
