import logging
from typing import Any

from fastapi import FastAPI
from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from tortoise.contrib.starlette import register_tortoise

from .feature_flags import FeatureFlags


def initialize_application() -> FastAPI:
    from config import application_config

    application = FastAPI(**application_config)
    return application


def initialize_sentry(application: FastAPI) -> FastAPI:
    from config import sentry_config
    from config import application_config
    from common.sentry import utils

    if not application_config["debug"]:
        sentry_init(
            dsn=sentry_config["dsn"],
            send_default_pii=sentry_config["send_default_pii"],
            before_send=utils.before_send,
            max_value_length=sentry_config["max_value_length"],
            # ignore_errors=['ExceptionGroup', ],
        )
        application: FastAPI = SentryAsgiMiddleware(application)
    return application


def initialize_redis(application: FastAPI) -> None:
    from common.redis import broker

    application.on_event("startup")(broker.connect)
    application.on_event("shutdown")(broker.disconnect)


def initialize_database(application: FastAPI) -> None:
    from config import tortoise_config

    register_tortoise(application, config=tortoise_config)


def initialize_routers(application: FastAPI) -> None:
    from config.routers import get_routers

    for router in get_routers():
        application.include_router(router)


def initialize_exceptions(application: FastAPI) -> None:
    from config.exceptions import get_exceptions

    for exception, handler in get_exceptions().items():
        application.add_exception_handler(exception, handler)


def initialize_middlewares(application: FastAPI) -> None:
    from config.middlewares import get_middlewares

    for item in get_middlewares():
        middleware: object = item[0]
        options: dict[str, Any] = item[1]
        application.add_middleware(middleware, **options)


def initialize_websockets(application: FastAPI) -> None:
    from config.websockets import get_websockets

    for websocket, path in get_websockets().items():
        application.websocket(path)(websocket)


def initialize_logger() -> None:
    from common.loggers import LOGGER_CONFIG, STRUCTLOG_CONFIG
    import logging.config
    import structlog
    logging.config.dictConfig(LOGGER_CONFIG)
    structlog.configure(**STRUCTLOG_CONFIG)


def initialize_unleash(application: FastAPI) -> None:
    from common.unleash.client import UnleashClient

    client = UnleashClient()
    application.unleash = client
    application.feature_flags = FeatureFlags
    logging.getLogger('apscheduler.executors.default').propagate = False
