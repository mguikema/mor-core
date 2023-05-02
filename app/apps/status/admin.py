from apps.status.models import Status
from django.contrib import admin


class StatusAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "naam",
        "aangemaakt_op",
        "melding",
    )


admin.site.register(Status, StatusAdmin)
