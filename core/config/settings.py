import os
import sys
from os.path import join

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
LANGUAGE_CODE = "nl-NL"

DEFAULT_ALLOWED_HOSTS = "localhost,127.0.0.1"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", DEFAULT_ALLOWED_HOSTS).split(",")

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
    "rest_framework",
    "django_filters",
    "corsheaders",
    "django_extensions",
    "django_spaghetti",
    "health_check",
    "health_check.cache",
    "health_check.storage",
    # Apps
    "apps.mor",
    "apps.health",
)

MIDDLEWARE = (
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "csp.middleware.CSPMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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

# Database settings
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST_OVERRIDE")
DATABASE_PORT = os.getenv("DATABASE_PORT_OVERRIDE")

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": DATABASE_NAME,  # noqa:
        "USER": DATABASE_USER,  # noqa
        "PASSWORD": DATABASE_PASSWORD,  # noqa
        "HOST": DATABASE_HOST,  # noqa
        "PORT": DATABASE_PORT,  # noqa
    },
}  # noqa

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

SITE_ID = 1
SITE_NAME = os.getenv("SITE_NAME", "MOR CORE")
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "localhost")

# Django REST framework settings
REST_FRAMEWORK = dict(
    PAGE_SIZE=100,
    UNAUTHENTICATED_USER={},
    UNAUTHENTICATED_TOKEN={},
    DEFAULT_PAGINATION_CLASS="rest_framework.pagination.LimitOffsetPagination",
    DEFAULT_FILTER_BACKENDS=("django_filters.rest_framework.DjangoFilterBackend",),
    DEFAULT_THROTTLE_RATES={
        "nouser": os.getenv("PUBLIC_THROTTLE_RATE", "60/hour"),
    },
    # DEFAULT_RENDERER_CLASSES=(
    #     "rest_framework.renderers.JSONRenderer",
    #     "rest_framework.renderers.BrowsableAPIRenderer",
    # ),
)

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
    "http://cdnjs.cloudflare.com/ajax/libs/vis/4.7.0/vis.min.js",
)
CSP_IMG_SRC = ("'self'", "data:")
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://cdnjs.cloudflare.com/ajax/libs/vis/4.7.0/vis.min.css",
)
CSP_CONNECT_SRC = ("'self'",)

SPAGHETTI_SAUCE = {
    "apps": [
        "mor",
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
                "django.template.context_processors.request",
            ],
        },
    }
]

# REDIS_URL = "redis://redis:6379"
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": REDIS_URL,
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             "SOCKET_CONNECT_TIMEOUT": 5,
#             "SOCKET_TIMEOUT": 5,
#         },
#     }
# }

# SESSION_ENGINE = "django.contrib.sessions.backends.cache"

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
