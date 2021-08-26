import logging
import logging.config
import os.path as path

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(levelname)s - %(message)s"
        },
        "detail": {
            "format": "%(asctime)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "debugfile": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": f"{path.dirname(path.abspath(__file__))}/../logs/debug.log",
            "encoding": "utf8"
        },
        "errorfile": {
            "class": "logging.FileHandler",
            "level": "ERROR",
            "formatter": "detail",
            "filename": f"{path.dirname(path.abspath(__file__))}/../logs/error.log",
            "encoding": "utf8"
        }
    },
    "loggers": {
        "basic": {
            "level": "DEBUG",
            "handlers": [
                "debugfile", "errorfile"
            ],
            "propagate": False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger("basic")
