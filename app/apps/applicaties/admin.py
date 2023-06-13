from apps.applicaties.models import Applicatie
from django.contrib import admin, messages
from django.core.cache import cache


class TaakapplicatieAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "naam",
        "gebruiker",
        "melding_context",
    )

    def save_model(self, request, obj, form, change):
        if obj.pk:
            cache.delete(obj.get_token_cache_key())
            orig_obj = Applicatie.objects.get(pk=obj.pk)
            if (
                obj.applicatie_gebruiker_wachtwoord
                != orig_obj.applicatie_gebruiker_wachtwoord
            ):
                obj.encrypt_applicatie_gebruiker_wachtwoord(
                    obj.applicatie_gebruiker_wachtwoord
                )

        elif obj.applicatie_gebruiker_wachtwoord:
            obj.encrypt_applicatie_gebruiker_wachtwoord(
                obj.applicatie_gebruiker_wachtwoord
            )

        try:
            if obj._get_token():
                messages.success(request, "Connectie met de applicatie is gelukt")
            else:
                messages.error(request, "Connectie met de applicatie is mislukt!")
        except Exception:
            messages.error(request, "Connectie met de applicatie is mislukt!")

        obj.save()


admin.site.register(Applicatie, TaakapplicatieAdmin)
