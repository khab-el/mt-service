import logging
import sys
from logging.config import dictConfig

from src.settings import settings

LOG_CONFIG = dict(
    version=1,
    disable_existing_loggers=False,
    formatters={
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] [info:%(filename)s:%(funcName)s:%(lineno)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        },
    },
    handlers={
        "stdout_default": {
            "class": "logging.StreamHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "generic",
            "stream": sys.stdout,
        },
    },
    loggers={
        "": {
            "level": settings.LOG_LEVEL_ROOT,
            "propagate": False,
            "handlers": ["stdout_default"]
        },
        "asyncio": {
            "level": settings.LOG_LEVEL_ASYNCIO,
            "propagate": False,
            "handlers": ["stdout_default"]
        },
        "uvicorn.access": {
            "level": "INFO",
            "propagate": False,
            "handlers": ["stdout_default"],
        },
        "api": {
            "level": "DEBUG",
            "propagate": False,
            "handlers": ["stdout_default"],
        },
        "consume": {
            "level": "DEBUG",
            "propagate": False,
            "handlers": ["stdout_default"],
        }
    },
)
log_config = dictConfig(LOG_CONFIG)


def get_logger(name, level=logging.DEBUG):
    """
    Return logger with conf
    """
    log = logging.getLogger(name)
    log.setLevel(level)
    return log
