from django.apps import AppConfig


class ApplicatiesConfig(AppConfig):
    name = "apps.applicaties"
    verbose_name = "Applicaties"

    def ready(self):
        import apps.applicaties.signal_receivers  # noqa
