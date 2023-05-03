from apps.classificatie.viewsets import OnderwerpViewSet
from apps.mor.views import serve_media
from apps.mor.viewsets import (
    BijlageViewSet,
    MelderViewSet,
    MeldingContextViewSet,
    MeldingGebeurtenisTypeViewSet,
    MeldingGebeurtenisViewSet,
    MeldingViewSet,
    SignaalViewSet,
    TaakApplicatieViewSet,
)
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django_db_schema_renderer.urls import schema_urls
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r"bijlage", BijlageViewSet, basename="bijlage")
# router.register(r"taak-applicatie", TaakApplicatieViewSet, basename="taak_applicatie")
# router.register(
#     r"melding-gebeurtenis-type",
#     MeldingGebeurtenisTypeViewSet,
#     basename="melding_gebeurtenis_type",
# )
# router.register(
#     r"melding-gebeurtenis", MeldingGebeurtenisViewSet, basename="melding_gebeurtenis"
# )
# router.register(r"geometrie", GeometrieViewSet, basename="geometrie")
router.register(r"signaal", SignaalViewSet, basename="signaal")
router.register(r"melding-context", MeldingContextViewSet, basename="melding_context")
router.register(r"melding", MeldingViewSet, basename="melding")
# router.register(r"melder", MelderViewSet, basename="melder")
router.register(r"onderwerp", OnderwerpViewSet, basename="onderwerp")

urlpatterns = [
    path("v1/", include((router.urls, "app"), namespace="v1")),
    path("api-token-auth/", views.obtain_auth_token),
    path("health/", include("health_check.urls")),
    path("db-schema/", include((schema_urls, "db-schema"))),
    path("plate/", include("django_spaghetti.urls")),
    # The Django admin
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    re_path(r"^media", serve_media, name="protected_media"),
    path("", include("django_prometheus.urls")),
]

if settings.DEBUG:
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
