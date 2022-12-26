# flake8: noqa
import os

from .common import (
    AUTHENTICATION_BACKENDS,
    BASE_DIR,
    DEBUG,
    DEFAULT_AUTO_FIELD,
    INSTALLED_APPS,
    MIDDLEWARE,
    TEMPLATES,
    TIME_ZONE,
    USE_TZ,
    WSGI_APPLICATION,
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "ID309280_secretariaat",
    }
}

FIXTURE_DIRS = ["management/tests/fixtures"]
