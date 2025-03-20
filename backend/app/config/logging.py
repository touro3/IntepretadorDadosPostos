import logging
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s"}
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/app.log",
            "formatter": "standard",
        },
    },
    "loggers": {
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "fastapi": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "app_logger": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("intec")
