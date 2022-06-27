from ecommerce.settings.base import *

ENV = "development"

########### .env-based keys #################

SECRET_KEY = config["SECRET_KEY"]
POSTGRES_PASSWORD = config["POSTGRES_PASSWORD"]
POSTGRES_USER = config["POSTGRES_USER"]
POSTGRES_DB = config["POSTGRES_DB"]
PAYPAL_CLIENT_ID = config["PAYPAL_CLIENT_ID"]
PAYPAL_SECRET = config["PAYPAL_SECRET"]
PAYPAL_BUSINESS_EMAIL = config["PAYPAL_BUSINESS_EMAIL"]
PAYPAL_BUSINESS_PASSWORD = config["PAYPAL_BUSINESS_PASSWORD"]
PAYPAL_PERSONAL_EMAIL = config["PAYPAL_PERSONAL_EMAIL"]
PAYPAL_PERSONAL_PASSWORD = config["PAYPAL_PERSONAL_PASSWORD"]

###########  general configuration ##########

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql_psycopg2",
#         "NAME": config["POSTGRES_DB"],
#         "USER": config["POSTGRES_USER"],
#         "PASSWORD": config["POSTGRES_PASSWORD"],
#         "HOST": "localhost",
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []

STATIC_ROOT = BASE_DIR / "static_root/"
STATICFILES_DIRS = [
    BASE_DIR / "static/",
]

MEDIA_ROOT = BASE_DIR / "media/"

LOGGING = {
    "version": 1,
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"},
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "simple"},
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

SQUARE_APP_ID = "sandbox-sq0idb-tm1Xf8oX6Jshm4UElKDG6A"
SQUARE_LOCATION_ID = "LCDT9FPECTMHA"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

if DEBUG:
    # make all loggers use the console.
    # for logger in LOGGING["loggers"]:
    #     LOGGING["loggers"][logger]["handlers"] = ["console"]

    # django-debug-toolbar
    INSTALLED_APPS.append("django_extensions")
    INTERNAL_IPS = ("127.0.0.1",)
    MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)

    INSTALLED_APPS += ("debug_toolbar",)

    DEBUG_TOOLBAR_PANELS = [
        "debug_toolbar.panels.versions.VersionsPanel",
        "debug_toolbar.panels.timer.TimerPanel",
        "debug_toolbar.panels.settings.SettingsPanel",
        "debug_toolbar.panels.headers.HeadersPanel",
        "debug_toolbar.panels.request.RequestPanel",
        "debug_toolbar.panels.sql.SQLPanel",
        "debug_toolbar.panels.staticfiles.StaticFilesPanel",
        "debug_toolbar.panels.templates.TemplatesPanel",
        "debug_toolbar.panels.cache.CachePanel",
        "debug_toolbar.panels.signals.SignalsPanel",
        "debug_toolbar.panels.logging.LoggingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
    ]

    DEBUG_TOOLBAR_CONFIG = {
        "INTERCEPT_REDIRECTS": False,
    }
