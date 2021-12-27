import os
from pathlib import Path

from dotenv import dotenv_values
from ecommerce.settings.common import *

ENV = "staging"

BASE_DIR = Path(__file__).resolve().parent.parent
print(f"BASE_DIR set to {BASE_DIR}")

config = dotenv_values()  # loads .env from BASE_DIR by default

SECRET_KEY = config["SECRET_KEY"]

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "34.207.88.228", "transylvania.bostonmonks.com"]

WSGI_APPLICATION = "ecommerce.wsgi.application"

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

STATIC_ROOT = "/var/static_root"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_ROOT = "/var/media_root"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "/var/log/htmshop/django.log",
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

STRIPE_PUBLISHABLE_KEY = (
    "pk_live_51K6PnSCFIch5ayqkdmgTnL8Ahszdb6lvZX3VbCrEuCPocFFGjtjRfA8hQUfyMo1BbCBuECjBMIMFt31C37ynBa0j00zZ1YUG5v"
)
STRIPE_SECRET_KEY = config["STRIPE_SECRET_KEY"]