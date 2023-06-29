from apps.melders.models import Melder
from django.contrib import admin


class DefaultAdmin(admin.ModelAdmin):
    pass


admin.site.register(Melder, DefaultAdmin)
