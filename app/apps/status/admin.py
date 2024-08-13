from apps.status.models import Status
from django.contrib import admin


class StatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "naam",
        "aangemaakt_op",
        "melding",
    )
    raw_id_fields = ("melding",)
    search_fields = ("melding__id",)


admin.site.register(Status, StatusAdmin)
