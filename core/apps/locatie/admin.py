from apps.locatie.models import Adres, Geometrie, Graf, Locatie
from django.contrib import admin


class DefaultAdmin(admin.ModelAdmin):
    pass


admin.site.register(Graf, DefaultAdmin)
admin.site.register(Adres, DefaultAdmin)
admin.site.register(Locatie, DefaultAdmin)
admin.site.register(Geometrie, DefaultAdmin)
