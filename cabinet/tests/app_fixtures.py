import pytest
from fastapi import FastAPI
from tortoise.contrib.test import finalizer as finalize_database
from tortoise.contrib.test import initializer as initialize_database


@pytest.fixture(scope="session")
def application(database_modules: list[str], database_url: str):
    from config.initializers import (
        initialize_application,
        initialize_exceptions,
        initialize_sentry,
        initialize_websockets,
        initialize_routers
    )
    application: FastAPI = initialize_application()
    initialize_routers(application)
    initialize_exceptions(application)
    initialize_sentry(application)
    initialize_websockets(application)
    initialize_database(database_modules, db_url=database_url)

    yield application

    finalize_database()
