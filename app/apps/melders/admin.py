from apps.melders.models import Melder
from django.contrib import admin


class DefaultAdmin(admin.ModelAdmin):
    list_display = ("id", "naam", "signaal")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "signaal",
        )


admin.site.register(Melder, DefaultAdmin)
