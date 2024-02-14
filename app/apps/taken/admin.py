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
        "pretty_afhandeltijd",
        "melding",
        "status",
        "resolutie",
    )

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
