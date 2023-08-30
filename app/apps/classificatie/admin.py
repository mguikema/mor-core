from apps.classificatie.models import Onderwerp, OnderwerpGroep
from django.contrib import admin


class OnderwerpGroepAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )


class OnderwerpAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "onderwerp_groep")


admin.site.register(Onderwerp, OnderwerpAdmin)
admin.site.register(OnderwerpGroep, OnderwerpGroepAdmin)
