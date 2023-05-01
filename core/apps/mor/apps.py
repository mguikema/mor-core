from django.apps import AppConfig


class MORConfig(AppConfig):
    name = "apps.mor"
    verbose_name = "MOR modellen"

    def ready(self):
        import apps.mor.metrics_collectors  # noqa
        import apps.mor.signal_receivers  # noqa
