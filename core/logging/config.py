from pathlib import Path
from django.conf import settings

BASE_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },

    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

if settings.DEBUG:
    BASE_LOGGING["formatters"] = {
        "color": {
            "()": "core.logging.formatters.ColorFormatter",
            "format": "[{levelname}] {asctime} {name}: {message}",
            "style": "{",
        },
    }
    BASE_LOGGING["handlers"]["console"]["formatter"] = "color"

LOGGING = BASE_LOGGING