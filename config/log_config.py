import logging
import os
import sys
from logging.config import dictConfig

# 로그 디렉토리 설정
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "log"))
os.makedirs(LOG_DIR, exist_ok=True)


class FlushStreamHandler(logging.StreamHandler):
    """로그를 찍을 때마다 flush 보장"""

    def emit(self, record):
        super().emit(record)
        self.flush()


def setup_logging(log_filename: str, error_log_filename: str) -> logging.Logger:
    log_file = os.path.join(LOG_DIR, log_filename)
    error_log_file = os.path.join(LOG_DIR, error_log_filename)

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
                    "class": "config.log_config.FlushStreamHandler",
                    "formatter": "default",
                    "stream": sys.stdout,
                },
                "file": {
                    "level": "DEBUG",
                    "class": "logging.FileHandler",
                    "filename": log_file,
                    "formatter": "default",
                },
                "error_file": {
                    "level": "ERROR",
                    "class": "logging.FileHandler",
                    "filename": error_log_file,
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
