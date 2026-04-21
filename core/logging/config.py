from pathlib import Path
from backend.settings import DEBUG

BASE_DIR = Path(__file__).resolve().parent.parent.parent

if DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "color": {
                "()": "core.logging.formatters.ColorFormatter",
                "format": "[{levelname}] {asctime} {name}: {message}",
                "style": "{",
            },
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "color",
            },
        },

        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
    }

else:
    LOGGING = {
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