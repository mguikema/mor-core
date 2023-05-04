from django.apps import AppConfig


class MeldingenConfig(AppConfig):
    name = "apps.meldingen"
    verbose_name = "Meldingen"

    def ready(self):
        import apps.meldingen.metrics_collectors  # noqa
        import apps.meldingen.signal_receivers  # noqa
