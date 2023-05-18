from config.initializers import (
    initialize_application,
    initialize_database,
    initialize_exceptions,
    initialize_middlewares,
    initialize_redis,
    initialize_routers,
    initialize_sentry,
    initialize_websockets,
    initialize_logger
)
from fastapi import FastAPI


def get_fastapi_application() -> FastAPI:
    application: FastAPI = initialize_application()
    initialize_logger()
    initialize_database(application)
    initialize_redis(application)
    initialize_routers(application)
    initialize_middlewares(application)
    initialize_exceptions(application)
    initialize_sentry(application)
    initialize_websockets(application)
    application: FastAPI = application
    return application

