from apps.applicaties.viewsets import TaakapplicatieViewSet
from apps.bijlagen.viewsets import BijlageViewSet
from apps.classificatie.viewsets import OnderwerpViewSet
from apps.meldingen.views import serve_protected_media
from apps.meldingen.viewsets import MeldinggebeurtenisViewSet, MeldingViewSet
from apps.signalen.viewsets import SignaalViewSet
from apps.taken.viewsets import TaakgebeurtenisViewSet, TaakopdrachtViewSet
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
router.register(r"signaal", SignaalViewSet, basename="signaal")
router.register(r"melding", MeldingViewSet, basename="melding")
router.register(
    r"meldinggebeurtenis", MeldinggebeurtenisViewSet, basename="meldinggebeurtenis"
)
router.register(r"onderwerp", OnderwerpViewSet, basename="onderwerp")
router.register(r"applicatie", TaakapplicatieViewSet, basename="applicatie")
router.register(r"taakapplicatie", TaakapplicatieViewSet, basename="taakapplicatie")
router.register(r"taakopdracht", TaakopdrachtViewSet, basename="taakopdracht")
router.register(r"taakgebeurtenis", TaakgebeurtenisViewSet, basename="taakgebeurtenis")
router.register(r"bijlage", BijlageViewSet, basename="bijlage")

urlpatterns = [
    path("api/v1/", include((router.urls, "app"), namespace="v1")),
    path("api-token-auth/", views.obtain_auth_token),
    # path(
    #     "admin/login/",
    #     RedirectView.as_view(
    #         url="/oidc/authenticate/?next=/admin/",
    #         permanent=False,
    #     ),
    #     name="admin_login",
    # ),
    # path(
    #     "admin/logout/",
    #     RedirectView.as_view(
    #         url="/oidc/logout/?next=/admin/",
    #         permanent=False,
    #     ),
    #     name="admin_logout",
    # ),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("admin/", admin.site.urls),
    path("health/", include("health_check.urls")),
    path("db-schema/", include((schema_urls, "db-schema"))),
    path("plate/", include("django_spaghetti.urls")),
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
    re_path(r"^media", serve_protected_media, name="protected_media"),
    path("", include("django_prometheus.urls")),
]

if settings.DEBUG:
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
