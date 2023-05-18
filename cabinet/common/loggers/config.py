import sys

import structlog
from config import logs_dir

from .processors import (DelimiterProcessor, HistoryManagerProcessor,
                         SortKeysProcessor)

STRUCTLOG_CONFIG = dict(
    processors=[
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S", utc=False),
        structlog.contextvars.merge_contextvars,
        HistoryManagerProcessor(),
        structlog.processors.StackInfoRenderer(),
        SortKeysProcessor(keys=['method', 'view', 'request_id']),
        structlog.dev.ConsoleRenderer(colors=False, sort_keys=False),
        DelimiterProcessor()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

LOGGER_CONFIG = {
    "version": 1,
    'disable_existing_loggers': True,
    "formatters": {
        "default": {
            "format": "%(message)s",
        }
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": sys.stdout
        },
        "file_errors": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": logs_dir / "errors.log",
            "formatter": "default",
            "maxBytes": 1024 * 1024 * 1,  # 1 Mb
            "backupCount": 5,
        },
        "file_amocrm_secret": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": logs_dir / "amocrm-secret.log",
            "formatter": "default",
            "maxBytes": 1024 * 1024 * 1,  # 1 Mb
            "backupCount": 1,
        },
        "file_amocrm_access_deal": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": logs_dir / "amocrm-access_deal.log",
            "formatter": "default",
            "maxBytes": 1024 * 1024 * 1,  # 1 Mb
            "backupCount": 1,
        },
        "file_amocrm_date_deal": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": logs_dir / "amocrm-date_deal.log",
            "formatter": "default",
            "maxBytes": 1024 * 1024 * 1,  # 1 Mb
            "backupCount": 1,
        },
        "file_amocrm_deal_success": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": logs_dir / "amocrm-deal_success.log",
            "formatter": "default",
            "maxBytes": 1024 * 1024 * 1,  # 1 Mb
            "backupCount": 1,
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": True,
        },
        "errors": {
            "handlers": ["file_errors"],
            "level": "WARNING"
        },
        "amocrm_secret_hook": {
            "handlers": ["file_amocrm_secret"],
            "level": "INFO"
        },
        "amocrm_access_deal_hook": {
            "handlers": ["file_amocrm_access_deal"],
            "level": "INFO"
        },
        "amocrm_date_deal_hook": {
            "handlers": ["file_amocrm_date_deal"],
            "level": "INFO"
        },
        "amocrm_deal_success_hook": {
            "handlers": ["file_amocrm_deal_success"],
            "level": "INFO"
        },
    }
}
