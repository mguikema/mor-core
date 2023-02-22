from apps.mor.viewsets import TaakApplicatieViewSet
from django.contrib import admin
from django.urls import include, path
from django_db_schema_renderer.urls import schema_urls
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"taak-applicatie", TaakApplicatieViewSet, basename="taak_applicatie")

urlpatterns = [
    path("v1/", include((router.urls, "app"), namespace="v1")),
    path("health/", include("health_check.urls")),
    path("db-schema/", include((schema_urls, "db-schema"))),
    path("plate/", include("django_spaghetti.urls")),
    # The Django admin
    path("admin/", admin.site.urls),
]
