from apps.aliassen.models import OnderwerpAlias
from django.contrib import admin


class OnderwerpAliasAdmin(admin.ModelAdmin):
    list_display = ("id", "bron_url", "naam", "aangemaakt_op")

    def naam(self, obj):
        return obj.response_json.get("name", "")

    naam.short_description = "Naam"


admin.site.register(OnderwerpAlias, OnderwerpAliasAdmin)
