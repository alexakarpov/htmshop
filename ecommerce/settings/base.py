import os
from pathlib import Path

from dotenv import dotenv_values

print("workdir: ", os.getcwd())
BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(f"in {os.path.basename(__file__)}. BASE_DIR set to: {BASE_DIR}")

########### .env-based keys #################
config = dotenv_values(BASE_DIR / ".env")

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

LOGIN_REDIRECT_URL = "/account/dashboard"
LOGIN_URL = "/account/login/"
BASKET_SESSION_ID = "basket"

# Email setting
DEFAULT_FROM_EMAIL = "info@thehtm.org"
