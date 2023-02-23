from apps.mor.viewsets import (
    BijlageViewSet,
    GeometrieViewSet,
    MeldingGebeurtenisTypeViewSet,
    MeldingGebeurtenisViewSet,
    MeldingViewSet,
    SignaalViewSet,
    TaakApplicatieViewSet,
)
from django.contrib import admin
from django.urls import include, path
from django_db_schema_renderer.urls import schema_urls
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"bijlage", BijlageViewSet, basename="bijlage")
router.register(r"taak-applicatie", TaakApplicatieViewSet, basename="taak_applicatie")
router.register(
    r"melding-gebeurtenis-type",
    MeldingGebeurtenisTypeViewSet,
    basename="melding_gebeurtenis_type",
)
router.register(
    r"melding-gebeurtenis", MeldingGebeurtenisViewSet, basename="melding_gebeurtenis"
)
router.register(r"geometrie", GeometrieViewSet, basename="geometrie")
router.register(r"signaal", SignaalViewSet, basename="signaal")
router.register(r"melding", MeldingViewSet, basename="melding")

urlpatterns = [
    path("v1/", include((router.urls, "app"), namespace="v1")),
    path("health/", include("health_check.urls")),
    path("db-schema/", include((schema_urls, "db-schema"))),
    path("plate/", include("django_spaghetti.urls")),
    # The Django admin
    path("admin/", admin.site.urls),
]
