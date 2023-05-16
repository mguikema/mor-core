import locale
import os
import sys
from os.path import join

locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRUE_VALUES = [True, "True", "true", "1"]

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", os.environ.get("DJANGO_SECRET_KEY"))

ENVIRONMENT = os.getenv("ENVIRONMENT")
DEBUG = ENVIRONMENT == "development"

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

USE_TZ = True
TIME_ZONE = "Europe/Amsterdam"
USE_L10N = True
USE_I18N = False
LANGUAGE_CODE = "nl-NL"
LANGUAGES = [("nl", "Dutch")]

DEFAULT_ALLOWED_HOSTS = "localhost,127.0.0.1"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", DEFAULT_ALLOWED_HOSTS).split(",")

SIGNALEN_API = os.getenv("SIGNALEN_API")
MELDING_API = os.getenv("MELDING_API")
APPLICATIE_BASIS_URL = os.getenv("APPLICATIE_BASIS_URL")
ALLOW_UNAUTHORIZED_MEDIA_ACCESS = (
    os.getenv("ALLOW_UNAUTHORIZED_MEDIA_ACCESS", False) in TRUE_VALUES
)

INSTALLED_APPS = (
    "django_db_schema_renderer",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.gis",
    "django.contrib.postgres",
    "rest_framework",
    "rest_framework.authtoken",
    "drf_spectacular",
    "django_filters",
    "corsheaders",
    "django_extensions",
    "django_spaghetti",
    "health_check",
    "health_check.db",
    "health_check.contrib.migrations",
    "sorl.thumbnail",
    "debug_toolbar",
    "django_prometheus",
    "django_rename_app",
    # Apps
    "apps.meldingen",
    "apps.health",
    "apps.classificatie",
    "apps.locatie",
    "apps.status",
    "apps.aliassen",
    "apps.applicaties",
)


MIDDLEWARE = (
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "csp.middleware.CSPMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
)

# django-permissions-policy settings
PERMISSIONS_POLICY = {
    "accelerometer": [],
    "ambient-light-sensor": [],
    "autoplay": [],
    "camera": [],
    "display-capture": [],
    "document-domain": [],
    "encrypted-media": [],
    "fullscreen": [],
    "geolocation": [],
    "gyroscope": [],
    "interest-cohort": [],
    "magnetometer": [],
    "microphone": [],
    "midi": [],
    "payment": [],
    "usb": [],
}


STATIC_URL = "/static/"
STATIC_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), "static"))

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), "media"))

if DEBUG:
    import socket  # only if you haven't already imported this

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
        "127.0.0.1",
        "10.0.2.2",
    ]

# Database settings
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST_OVERRIDE")
DATABASE_PORT = os.getenv("DATABASE_PORT_OVERRIDE")

DEFAULT_DATABASE = {
    "ENGINE": "django.contrib.gis.db.backends.postgis",
    "NAME": DATABASE_NAME,  # noqa:
    "USER": DATABASE_USER,  # noqa
    "PASSWORD": DATABASE_PASSWORD,  # noqa
    "HOST": DATABASE_HOST,  # noqa
    "PORT": DATABASE_PORT,  # noqa
}

DATABASES = {
    "default": DEFAULT_DATABASE,
}
DATABASES.update(
    {
        "alternate": DEFAULT_DATABASE,
    }
    if ENVIRONMENT == "test"
    else {}
)

if ENVIRONMENT == "test":
    DJANGO_TEST_USERNAME = os.getenv("DJANGO_TEST_USERNAME", "test")
    DJANGO_TEST_EMAIL = os.getenv("DJANGO_TEST_EMAIL", "test@test.com")
    DJANGO_TEST_PASSWORD = os.getenv("DJANGO_TEST_PASSWORD", "insecure")

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

SITE_ID = 1
SITE_NAME = os.getenv("SITE_NAME", "MOR CORE")
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "localhost")

# Django REST framework settings
REST_FRAMEWORK = dict(
    PAGE_SIZE=5,
    UNAUTHENTICATED_USER={},
    UNAUTHENTICATED_TOKEN={},
    DEFAULT_PAGINATION_CLASS="utils.pagination.LimitOffsetPagination",
    DEFAULT_FILTER_BACKENDS=("django_filters.rest_framework.DjangoFilterBackend",),
    DEFAULT_THROTTLE_RATES={
        "nouser": os.getenv("PUBLIC_THROTTLE_RATE", "60/hour"),
    },
    DEFAULT_PARSER_CLASSES=[
        "rest_framework.parsers.JSONParser",
        "utils.parsers.NestedMultipartParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ],
    DEFAULT_SCHEMA_CLASS="drf_spectacular.openapi.AutoSchema",
    DEFAULT_PERMISSION_CLASSES=("rest_framework.permissions.IsAuthenticated",),
    DEFAULT_AUTHENTICATION_CLASSES=("apps.auth.authentication.AuthenticationClass",),
)
SPECTACULAR_SETTINGS = {
    "TITLE": "MOR CORE",
    "DESCRIPTION": "Voor het organiseren en beheren van Meldingen Openbare Ruimte",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Django security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = "strict-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "SAMEORIGIN"
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True
CORS_ORIGIN_WHITELIST = ()
CORS_ORIGIN_ALLOW_ALL = False
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_NAME = "__Secure-sessionid" if not DEBUG else "sessionid"
CSRF_COOKIE_NAME = "__Secure-csrftoken" if not DEBUG else "csrftoken"
SESSION_COOKIE_SAMESITE = "Strict" if not DEBUG else "Lax"
CSRF_COOKIE_SAMESITE = "Strict" if not DEBUG else "Lax"

# Settings for Content-Security-Policy header
CSP_DEFAULT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",
    "blob:",
    "cdnjs.cloudflare.com",
    "cdn.jsdelivr.net",
)
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "cdn.redoc.ly",
    "cdn.jsdelivr.net",
    "map1c.vis.earthdata.nasa.gov",
    "map1b.vis.earthdata.nasa.gov",
    "map1a.vis.earthdata.nasa.gov",
)
CSP_STYLE_SRC = (
    "'self'",
    "data:",
    "'unsafe-inline'",
    "cdnjs.cloudflare.com",
    "cdn.jsdelivr.net",
    "fonts.googleapis.com",
)
CSP_CONNECT_SRC = ("'self'",)
CSP_FONT_SRC = (
    "'self'",
    "fonts.gstatic.com",
)

SPAGHETTI_SAUCE = {
    "apps": [
        "meldingen",
    ],
    "show_fields": False,
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.messages.context_processors.messages",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.static",
                "django.template.context_processors.request",
            ],
        },
    }
]

THUMBNAIL_BACKEND = "utils.images.ThumbnailBackend"
THUMBNAIL_PREFIX = "afbeeldingen-verkleind"
THUMBNAIL_KLEIN = "128x128"
BESTANDEN_PREFIX = "bestanden"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}
