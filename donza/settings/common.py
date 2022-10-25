"""
Django settings for donza project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

ADMINS = (("tim", "vanerum.tim@gmail.com"),)

MANAGERS = ADMINS

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "8488!@xxkp5)@4xef3#u2=sn+ydgolipy%8!c63g42+a(@rh=g"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    "management.apps.ManagementConfig",
    "phonenumber_field",
    "django_filters",
    "django_tables2",
    "bootstrap_modal_forms",
    "bootstrap4",
    "import_export",
    "localflavor",
    "guardian",
    "bulma",
    "django_extensions",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "global_login_required.GlobalLoginRequiredMiddleware",
]

ROOT_URLCONF = "donza.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "management.context_processors.authorized_ploegen",
                "management.context_processors.current_seizoen",
            ],
        },
    },
]

WSGI_APPLICATION = "donza.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

MYSQL_CONFIG = os.path.join(os.path.dirname(BASE_DIR), "config", "my.cnf")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "OPTIONS": {
            "read_default_file": MYSQL_CONFIG,
        },
        "NAME": "ID309280_secretariaat",
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

# Authentication backend
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",  # default
    "guardian.backends.ObjectPermissionBackend",
)

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Brussels"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

# Whitelist public pages
# Login page should be public, otherwise infinite redirection occurs
PUBLIC_PATHS = [
    r"^/accounts/login/*",
]

# Pagination loading
ENDLESS_PAGINATION_LOADING = """
    <div class="spinner small" style="margin:auto">
        <div class="block_1 spinner_block small"></div>
        <div class="block_2 spinner_block small"></div>
        <div class="block_3 spinner_block small"></div>
    </div>
"""

FIXTURE_DIRS = (os.path.join(os.path.dirname(BASE_DIR), "config", "fixtures"),)

# for the import_export package
IMPORT_EXPORT_USE_TRANSACTIONS = True

# set default type of auto-created primary keys
DEFAULT_AUTO_FIELD='django.db.models.AutoField'
