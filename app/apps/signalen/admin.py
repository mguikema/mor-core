from apps.signalen.models import Signaal
from django.contrib import admin


class SignaalAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "uuid",
        "signaal_url",
        "aangemaakt_op",
        "bron_id",
        "bron_signaal_id",
        "melding",
        "melder",
    )


admin.site.register(Signaal, SignaalAdmin)
