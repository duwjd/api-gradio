import logging
import os
import sys
from logging.config import dictConfig

# 로그 디렉토리 설정
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "log"))
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILENAME = "gemgem-ai-test.log"
ERROR_LOG_FILENAME = "gemgem-ai-test-error.log"

LOG_FILE = os.path.join(LOG_DIR, LOG_FILENAME)
ERROR_LOG_FILE = os.path.join(LOG_DIR, ERROR_LOG_FILENAME)


def setup_logging() -> logging.Logger:
    # 시간 포함된 포맷 설정
    logging.getLogger().handlers.clear()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] [%(levelname)s] [%(process)d] [%(module)s:%(lineno)d] %(message)s",
                },
                "guniconr-error": {
                    "format": "[%(asctime)s] [%(levelname)s] [%(process)d] [%(module)s:%(lineno)d] %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": sys.stdout,
                },
                "file": {
                    "level": "DEBUG",
                    "class": "logging.FileHandler",
                    "filename": LOG_FILE,
                    "formatter": "default",
                },
                "error_file": {
                    "level": "ERROR",
                    "class": "logging.FileHandler",
                    "filename": ERROR_LOG_FILE,
                    "formatter": "default",
                },
            },
            "loggers": {
                "app": {
                    "level": "DEBUG",
                    "handlers": ["console", "error_file"],
                    "propagate": False,
                },
                "gunicorn.error": {
                    "level": "ERROR",
                    "handlers": ["console", "file", "error_file"],
                    "propagate": False,
                },
                "gunicorn.access": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": "INFO",
                    "handlers": ["file"],
                    "propagate": False,
                },
                "alembic": {
                    "level": "INFO",
                    "handlers": ["console", "file", "error_file"],
                    "propagate": False,
                },
            },
        }
    )
