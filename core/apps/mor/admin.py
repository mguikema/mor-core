from apps.mor.models import (
    Geometrie,
    Melding,
    MeldingGebeurtenis,
    MeldingGebeurtenisType,
    Signaal,
    TaakApplicatie,
)
from django.contrib import admin


class DefaultAdmin(admin.ModelAdmin):
    pass


# admin.site.register(ProccessProposalTemplate, DefaultAdmin)
# admin.site.register(ProccessProposalItemTemplate, DefaultAdmin)
# admin.site.register(ProccessProposal, DefaultAdmin)
# admin.site.register(ProccessProposalItem, DefaultAdmin)
admin.site.register(TaakApplicatie, DefaultAdmin)
admin.site.register(MeldingGebeurtenisType, DefaultAdmin)
admin.site.register(MeldingGebeurtenis, DefaultAdmin)
admin.site.register(Melding, DefaultAdmin)
admin.site.register(Geometrie, DefaultAdmin)
admin.site.register(Signaal, DefaultAdmin)
