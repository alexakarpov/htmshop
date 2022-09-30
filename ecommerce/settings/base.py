import os
from pathlib import Path

from dotenv import dotenv_values

print("workdir: ", os.getcwd())
BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(f"in {os.path.basename(__file__)}. BASE_DIR set to: {BASE_DIR}")

########### .env-based keys #################
config = dotenv_values()

WSGI_APPLICATION = "ecommerce.wsgi.application"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ecommerce.apps.catalogue",
    "ecommerce.apps.accounts",
    "ecommerce.apps.orders",
    "ecommerce.apps.checkout",
    "ecommerce.apps.shipping",
    "ecommerce.apps.playground",
    "ecommerce.apps.inventory",
    "rest_framework",
    # "djpaypal",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CSRF_TRUSTED_ORIGINS = ["https://transylvania.bostonmonks.com"]

ROOT_URLCONF = "ecommerce.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "ecommerce.apps.catalogue.context_processors.categories",
                "ecommerce.apps.basket.context_processors.basket",
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    "ecommerce.apps.accounts.auth_backend.EmailAuthBackend",
    # seems to be required for Django admin interface
    "django.contrib.auth.backends.ModelBackend",
]

WSGI_APPLICATION = "ecommerce.wsgi.application"

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"

MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.Account"

LOGIN_REDIRECT_URL = "/accounts/dashboard"
LOGIN_URL = "/accounts/login/"
LOGOUT_REDIRECT_URL = LOGIN_URL
BASKET_SESSION_KEY = "basket"

# Email setting
DEFAULT_FROM_EMAIL = "info@thehtm.org"

# shipping tiers
MEDIA_MAIL = "usps_media_mail"
EXPEDITED = [
    "ups_next_day_air_saver",
    "fedex_standard_overnight",
]
FAST = [
    "ups_2nd_day_air",
    "fedex_2day_am",
    "fedex_2day",
]
REGULAR = [
    "usps_priority_mail",
    "usps_first_class_mail",
    "fedex_express_saver",
    "ups_3_day_select",
    "usps_parcel_select",
    "ups_ground",
    "fedex_home_delivery",
    "usps_first_class_mail"
]

# Shipping
SE_API_KEY = "TEST_pTjqOjvNiKsTgNXKGtLi1jWEzUuDadyhO4uLfQSzXWw"

USPS_ID = "se-660215"
FEDEX_ID = "se-660217"
UPS_ID = "se-660216"
