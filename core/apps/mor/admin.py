from apps.mor.models import (
    Bijlage,
    Bron,
    Geometrie,
    Graf,
    Melder,
    Melding,
    MeldingGebeurtenis,
    MeldingGebeurtenisType,
    Signaal,
    TaakApplicatie,
)
from django.contrib import admin


class DefaultAdmin(admin.ModelAdmin):
    pass


admin.site.register(TaakApplicatie, DefaultAdmin)
admin.site.register(MeldingGebeurtenisType, DefaultAdmin)
admin.site.register(MeldingGebeurtenis, DefaultAdmin)
admin.site.register(Melding, DefaultAdmin)
admin.site.register(Graf, DefaultAdmin)
admin.site.register(Geometrie, DefaultAdmin)
admin.site.register(Signaal, DefaultAdmin)
admin.site.register(Bijlage, DefaultAdmin)
admin.site.register(Melder, DefaultAdmin)
admin.site.register(Bron, DefaultAdmin)
