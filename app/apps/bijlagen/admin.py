from apps.bijlagen.tasks import task_aanmaken_afbeelding_versies
from apps.meldingen.models import Bijlage
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


admin.site.register(Bijlage, BijlageAdmin)
