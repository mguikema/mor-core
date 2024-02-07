from apps.melders.models import Melder
from django.contrib import admin


class DefaultAdmin(admin.ModelAdmin):
    list_display = ("id", "naam", "signaal")


admin.site.register(Melder, DefaultAdmin)
