from django.apps import AppConfig
from health_check.plugins import plugin_dir


class HealthConfig(AppConfig):
    name = "apps.health"
    verbose_name = "Health"

    def ready(self):
        from apps.health.custom_checks import ApplicatieTokenAPIHealthCheck

        plugin_dir.register(ApplicatieTokenAPIHealthCheck)
