from apps.status.models import Status
from django.contrib import admin


class StatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "naam",
        "aangemaakt_op",
        "aangemaakt_op_ts",
        "melding",
    )
    raw_id_fields = ("melding",)
    search_fields = ("melding__id",)

    def aangemaakt_op_ts(self, obj):
        return obj.aangemaakt_op.timestamp()


admin.site.register(Status, StatusAdmin)
