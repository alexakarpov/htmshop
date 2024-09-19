from pathlib import Path

from dotenv import dotenv_values

# print("workdir: ", os.getcwd())
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# print(f"in {os.path.basename(__file__)}. BASE_DIR set to: {BASE_DIR}")

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
    "ecommerce.apps.inventory",
    "rangefilter",
    "rest_framework",
    "mptt",
    "simple_history",
    # "wkhtmltopdf",
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
    "simple_history.middleware.HistoryRequestMiddleware",
]

CSRF_TRUSTED_ORIGINS = [
    "https://transylvania.bostonmonks.com",
    "http://localhost:8000",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://transylvania.bostonmonks.com",
]

SQUARE_ACCESS_TOKEN = config["SQUARE_ACCESS_TOKEN"]

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
                # "ecommerce.apps.catalogue.context_processors.categories",
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

STATIC_URL = "static/"

MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.Account"

LOGIN_REDIRECT_URL = "/accounts/dashboard"
LOGIN_URL = "/accounts/login/"
LOGOUT_REDIRECT_URL = "/"
BASKET_SESSION_KEY = "basket"

# Email setting
DEFAULT_FROM_EMAIL = "info@thehtm.org"

# shipping tiers
MEDIA_MAIL = "usps_media_mail"

# Shipping

SE_ENABLED = True  # otherwise, SS
EXPRESS = [
    "ups_next_day_air_saver",
    "fedex_standard_overnight",
]
FAST = [
    "ups_2nd_day_air",
    "usps_priority_mail_express",
    "fedex_2day_am",
    "fedex_2day",
]
REGULAR = [
    "usps_priority_mail",
    "usps_ground_advantage",
    "usps_first_class_mail",
    "fedex_express_saver",
    "ups_3_day_select",
    "usps_parcel_select",
    "ups_ground",
    "fedex_home_delivery",
    "usps_first_class_mail",
]

INTL_REGULAR = {
    "usps_first_class_mail_international",
    "globalpost_economy",
    "ups_standard_international",
}

INTL_FAST = {
    "ups_worldwide_expedited",
    "usps_priority_mail_international",
    "usps_priority_mail_express_international",
    "globalpost_priority",
    "gp_plus",
}

INTL_EXPRESS = {
    "ups_worldwide_express",
    "ups_worldwide_express_plus",
    "ups_worldwide_saver",
}

SE_API_KEY = config["SE_API_KEY"]
SS_GET_RATES_URL = "https://ssapi.shipstation.com/shipments/getrates"

USPS_ID = "se-660215"
FEDEX_ID = "se-660217"
UPS_ID = "se-660216"

# Item sets
SETS = {
    "A-420": [
        "A-429",
        "A-430",
        "A-431",
        "A-432",
        "A-421",
        "A-422",
        "A-423",
        "A-424",
        "A-425",
        "A-426",
        "A-427",
        "A-428",
    ],
    "A-420.11x14M": [
        "A-429.11x14M",
        "A-430.11x14M",
        "A-431.11x14M",
        "A-432.11x14M",
        "A-421.11x14M",
        "A-422.11x14M",
        "A-423.11x14M",
        "A-424.11x14M",
        "A-425.11x14M",
        "A-426.11x14M",
        "A-427.11x14M",
        "A-428.11x14M",
    ],
    # GF regular size
    "G-33": [
        "A-163",
        "A-174",
        "A-166",
        "A-161",
        "A-170",
        "A-176",
        "A-165",
        "A-162",
        "A-169",
        "A-177",
        "A-178",
        "A-172",
        "A-164",
        "A-175",
        "A-168",
        "A-171",
        "A-173",
        "A-167",
    ],
    # GF large size
    "G-27": [
        "A-163.11x14M",
        "A-174.11x14M",
        "A-166.11x14M",
        "A-161.11x14M",
        "A-170.11x14M",
        "A-176.11x14M",
        "A-165.11x14M",
        "A-162.11x14M",
        "A-169.11x14M",
        "A-177.11x14M",
        "A-178.11x14M",
        "A-172.11x14M",
        "A-164.11x14M",
        "A-175.11x14M",
        "A-168.11x14M",
        "A-171.11x14M",
        "A-173.11x14M",
        "A-167.11x14M",
    ],
}
