from apps.classificatie.models import Onderwerp
from django.contrib import admin


class DefaultAdmin(admin.ModelAdmin):
    pass


admin.site.register(Onderwerp, DefaultAdmin)
