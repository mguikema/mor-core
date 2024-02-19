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


@admin.action(description="Zet taak afgesloten_op voor afgesloten meldingen")
def action_set_taak_afgesloten_op_for_melding_afgesloten(modeladmin, request, queryset):
    for taakopdracht in queryset.all():
        if taakopdracht.melding.afgesloten_op and not taakopdracht.afgesloten_op:
            taakopdracht.afgesloten_op = taakopdracht.melding.afgesloten_op
            taakopdracht.save()


class TaakopdrachtAdmin(admin.ModelAdmin):
    list_editable = ("taaktype", "taak_url")
    list_display = (
        "id",
        "taaktype",
        "taak_url",
        # "uuid",
        "titel",
        "aangepast_op",
        "afgesloten_op",
        "melding__afgesloten_op",
        "afhandeltijd",
        "pretty_afhandeltijd",
        "melding",
        "status",
        "resolutie",
    )
    actions = (action_set_taak_afgesloten_op_for_melding_afgesloten,)
    readonly_fields = (
        "pretty_afhandeltijd",
        "aangemaakt_op",
        "aangepast_op",
        "afgesloten_op",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "titel",
                    "melding",
                    "applicatie",
                    "taaktype",
                    "status",
                    "resolutie",
                    "bericht",
                    "additionele_informatie",
                    "taak_url",
                )
            },
        ),
        (
            "Tijden",
            {
                "fields": (
                    "aangemaakt_op",
                    "aangepast_op",
                    "afgesloten_op",
                    "pretty_afhandeltijd",
                    "afhandeltijd",
                )
            },
        ),
    )

    def melding__afgesloten_op(self, obj):
        if obj.melding.afgesloten_op:
            return obj.melding.afgesloten_op
        else:
            return "-"

    def pretty_afhandeltijd(self, obj):
        if obj.afhandeltijd:
            days = obj.afhandeltijd.days
            total_seconds = obj.afhandeltijd.total_seconds()
            hours, remainder = divmod(total_seconds, 3600)
            remaining_hours = int(hours) % 24  # Remaining hours in the current day
            minutes, _ = divmod(remainder, 60)
            return f"{days} dagen, {remaining_hours} uur, {int(minutes)} minuten"
        else:
            return "-"

    pretty_afhandeltijd.short_description = "Afhandeltijd"


admin.site.register(Taakopdracht, TaakopdrachtAdmin)
admin.site.register(Taakgebeurtenis, TaakgebeurtenisAdmin)
