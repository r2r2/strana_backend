import pytest
from fastapi import FastAPI


@pytest.fixture(scope="session")
def application(redis):
    from config.initializers import (
        initialize_application,
        initialize_exceptions,
        initialize_routers,
        initialize_unleash,
    )
    application: FastAPI = initialize_application()
    initialize_routers(application)
    initialize_exceptions(application)
    initialize_unleash(application)

    yield application
