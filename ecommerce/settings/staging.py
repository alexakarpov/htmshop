from ecommerce.settings.base import *

ENV = "staging"

SECRET_KEY = config["SECRET_KEY"]

POSTGRES_PASSWORD = config["POSTGRES_PASSWORD"]
POSTGRES_USER = config["POSTGRES_USER"]
POSTGRES_DB = config["POSTGRES_DB"]

# PAYPAL_CLIENT_ID = config["PAYPAL_CLIENT_ID"]
# PAYPAL_SECRET = config["PAYPAL_SECRET"]
# PAYPAL_BUSINESS_EMAIL = config["PAYPAL_BUSINESS_EMAIL"]
# PAYPAL_BUSINESS_PASSWORD = config["PAYPAL_BUSINESS_PASSWORD"]
# PAYPAL_PERSONAL_EMAIL = config["PAYPAL_PERSONAL_EMAIL"]
# PAYPAL_PERSONAL_PASSWORD = config["PAYPAL_PERSONAL_PASSWORD"]

###########  general configuration ##########

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "52.201.215.80", "transylvania.bostonmonks.com"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config["POSTGRES_DB"],
        "USER": config["POSTGRES_USER"],
        "PASSWORD": config["POSTGRES_PASSWORD"],
        "HOST": "localhost",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

STATIC_ROOT = "/var/static_root/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_ROOT = "/var/media_root/"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "/var/htmshop/log/django.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

SQUARE_LOCATION_ID = "LCDT9FPECTMHA"
SQUARE_APP_ID = "sandbox-sq0idb-H9U7rreVn5iRv9za5FSlRg"

# email
EMAIL_BACKEND = "django_ses.SESBackend"
AWS_ACCESS_KEY_ID = "AKIA47CWFIGAWBLREFV6"
AWS_SECRET_ACCESS_KEY = config["AWS_SECRET_ACCESS_KEY"]
AWS_SES_REGION_NAME = "us-east-1"
AWS_SES_REGION_ENDPOINT = "email.us-east-1.amazonaws.com"

# Shipping related
USPS_ID = "se-660215"
UPS_ID = "se-660216"
FEDEX_ID = "se-660217"
