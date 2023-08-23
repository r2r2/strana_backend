import pytest
from fastapi import FastAPI


@pytest.fixture(scope="session")
def application():
    from config.initializers import (
        initialize_application,
        initialize_exceptions,
        initialize_sentry,
        initialize_websockets,
        initialize_routers,
    )
    application: FastAPI = initialize_application()
    initialize_routers(application)
    initialize_exceptions(application)
    initialize_sentry(application)
    initialize_websockets(application)

    yield application
