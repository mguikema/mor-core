from apps.aliassen.models import OnderwerpAlias
from django.contrib import admin


class OnderwerpAliasAdmin(admin.ModelAdmin):
    list_display = ("id", "bron_url", "aangemaakt_op")


admin.site.register(OnderwerpAlias, OnderwerpAliasAdmin)
