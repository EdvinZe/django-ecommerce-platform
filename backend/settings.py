from pathlib import Path
import logging
import os
from dotenv import load_dotenv
from django.conf.global_settings import AUTH_USER_MODEL, CSRF_TRUSTED_ORIGINS, MEDIA_ROOT, MEDIA_URL, STATICFILES_DIRS
from core.logging.config import LOGGING
from django.utils.translation import gettext_lazy as _


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING = LOGGING

# DEMO MODE
DEMO_MODE = os.getenv("DEMO_MODE", "False").lower() == "true"


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True").lower() == "true"


SITE_URL = os.getenv("SITE_URL")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")


CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'phonenumber_field',
    "rest_framework",
    "debug_toolbar",

    'pages',
    'products',
    'cart',
    'users',
    'pass_change',
    'orders',
    'lockers',
    'notifications',
    'api',
    'manager',
    'payments',
    'site_settings',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates', 'templates/includes'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "cart.context_processors.carts",
                "site_settings.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Load environment variables from .env to keep secrets out of source code
VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
VAPID_EMAIL = os.getenv("VAPID_EMAIL")

VAPID_CLAIMS = {
    "sub": os.getenv("VAPID_EMAIL")
}

# Database

DB_ENGINE = os.getenv("DB_ENGINE", "postgres")

if DB_ENGINE == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
        }
    }

# APIS
# STRIPE
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")

STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")

STRIPE_WEBHOOK_SECRET_KEY = os.getenv("STRIPE_WEBHOOK_SECRET_KEY")


# OMNIVA
OMNIVA_USERNAME = os.getenv("OMNIVA_USERNAME")

OMNIVA_PASSWORD = os.getenv("OMNIVA_PASSWORD")

OMNIVA_BASE_URL = os.getenv("OMNIVA_BASE_URL")

OMNIVA_LOCKERS_URL = os.getenv("OMNIVA_LOCKERS_URL")

# DPD
DPD_USERNAME = os.getenv("DPD_USERNAME")

DPD_PASSWORD = os.getenv("DPD_PASSWORD")

DPD_CLIENT_ID = os.getenv("DPD_CLIENT_ID")

DPD_TOKEN = os.getenv("DPD_TOKEN")

DPD_BASE_URL = os.getenv("DPD_BASE_URL")


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



LANGUAGE_CODE = "lt"

TIME_ZONE = "Europe/Vilnius"

LANGUAGES = [
    ("lt", _("Lithuanian")),
]

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / "static"
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'users.User'

# email settings
if DEMO_MODE:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.getenv("EMAIL_HOST")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS") == "True"

    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")


CACHE_NAMESPACE = "myapp:v1"

if DEMO_MODE:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
# Pickup status

ENABLE_PICKUP = False