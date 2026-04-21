from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "color": {
            "()": "core.logging.formatters.ColorFormatter",
            "format": "[{levelname}] {asctime} {name}: {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname}] {asctime} {name}: {message}",
            "style": "{",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "color",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs/app.log",
            "formatter": "simple",
            "level": "INFO",
        },
        "error_file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs/errors.log",
            "formatter": "simple",
            "level": "ERROR",
        },
    },

    "root": {
        "handlers": ["console", "file", "error_file"],
        "level": "INFO",
    },

    "loggers": {
        "django.utils.autoreload": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}