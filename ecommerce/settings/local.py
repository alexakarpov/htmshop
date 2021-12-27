import os
from pathlib import Path

from dotenv import dotenv_values

from .common import *

ENV = "development"

print("workdir: ", os.getcwd())
BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(f"BASE_DIR: {BASE_DIR}")

config = dotenv_values("devops/secrets/development.env")
SECRET_KEY = config["SECRET_KEY"]
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config["POSTGRES_DB"],
        "USER": config["POSTGRES_USER"],
        "PASSWORD": config["POSTGRES_PASSWORD"],
        "HOST": "localhost",
    }
}


AUTH_PASSWORD_VALIDATORS = []

STATIC_ROOT = BASE_DIR / "static_root"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

MEDIA_ROOT = BASE_DIR / "media/"

LOGGING = {
    "version": 1,
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"},
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {"level": "INFO", "class": "logging.StreamHandler", "formatter": "simple"},
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

STRIPE_PUBLISHABLE_KEY = (
    "pk_test_51K6PnSCFIch5ayqknnamJA9P1lEBHAft8RXXVPKYIEtciJKZbBRoS7Rt1mfbtFof1VCHdEd0Ax5OovOZDxRnz0QA00YsK7ehAb"
)
STRIPE_SECRET_KEY = config["STRIPE_SECRET_KEY"]


if DEBUG:
    # make all loggers use the console.
    for logger in LOGGING["loggers"]:
        LOGGING["loggers"][logger]["handlers"] = ["console"]
