import os
from pathlib import Path

from dotenv import dotenv_values
from ecommerce.settings.common import *

ENV = "staging"

print("workdir: ", os.getcwd())
BASE_DIR = Path(__file__).resolve().parent.parent
print(f"BASE_DIR set to {BASE_DIR}")

########### .env-based keys #################
config = dotenv_values()
SECRET_KEY = config["SECRET_KEY"]
STRIPE_SECRET_KEY = config["STRIPE_SECRET_KEY"]
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
    # {
    #     "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    # },
    # {
    #     "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    # },
    # {
    #     "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    # },
    # {
    #     "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    # },
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

# Stripe
STRIPE_PUBLISHABLE_KEY = (
    "pk_live_51K6PnSCFIch5ayqkdmgTnL8Ahszdb6lvZX3VbCrEuCPocFFGjtjRfA8hQUfyMo1BbCBuECjBMIMFt31C37ynBa0j00zZ1YUG5v"
)
STRIPE_SECRET_KEY = config["STRIPE_SECRET_KEY"]
STRIPE_LIVE_MODE = False  # Change to True in production

# Paypal
PAYPAL_CLIENT_ID = config["PAYPAL_CLIENT_ID"]
PAYPAL_SECRET = config["PAYPAL_SECRET"]
PAYPAL_BUSINESS_EMAIL = config["PAYPAL_BUSINESS_EMAIL"]
PAYPAL_BUSINESS_PASSWORD = config["PAYPAL_BUSINESS_PASSWORD"]
PAYPAL_PERSONAL_EMAIL = config["PAYPAL_PERSONAL_EMAIL"]
PAYPAL_PERSONAL_PASSWORD = config["PAYPAL_PERSONAL_PASSWORD"]

# email
EMAIL_BACKEND = "django_ses.SESBackend"
AWS_ACCESS_KEY_ID = config["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = config["AWS_SECRET_ACCESS_KEY"]
AWS_SES_REGION_NAME = "us-east-1"
AWS_SES_REGION_ENDPOINT = "email.us-east-1.amazonaws.com"
