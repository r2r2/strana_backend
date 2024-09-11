# pylint: disable=unused-argument

import asyncio
import logging
from typing import AsyncGenerator, Generator

import pytest
from _pytest.monkeypatch import MonkeyPatch
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from pytest import LogCaptureFixture

from src.core.logger import LoggerName, get_logger
from src.core.types import LoggerType

pytest_plugins = ["tests.fixtures"]


@pytest.fixture(
    name="logger",
    scope="session",
)
def logger_fixture() -> LoggerType:
    return get_logger(LoggerName.TESTS)


@pytest.fixture(
    name="event_loop",
    scope="session",
)
def event_loop_fixture() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(
    name="monkeypatch_session",
    scope="session",
)
def monkeypatch_session_fixture() -> Generator[MonkeyPatch, None, None]:
    monkey_patcher = MonkeyPatch()
    yield monkey_patcher
    monkey_patcher.undo()


@pytest.fixture(
    scope="function",
    autouse=True,
)
def logs_config(caplog: LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG, logger="tests")
    caplog.set_level(logging.WARNING, logger="httpx")
    caplog.set_level(logging.WARNING, logger="asyncio")


@pytest.fixture(
    name="patch_external_services",
    scope="session",
)
async def patch_external_services_fixture(
    monkeypatch_session: MonkeyPatch,
) -> None: ...


# @pytest.fixture(
#     name="app",
#     scope="session",
# )
# def app_fixture(
#     event_loop: asyncio.AbstractEventLoop,
#     patch_external_services: None,
# ) -> Generator[FastAPI, None, None]:
#     yield CombinedAppFactory(get_logger()).create_app()


@pytest.fixture(
    name="app_lifespan",
    scope="session",
)
async def app_lifespan_fixture(
    app: FastAPI,
    event_loop: asyncio.AbstractEventLoop,
) -> AsyncGenerator[FastAPI, None]:
    async with LifespanManager(app, startup_timeout=60, shutdown_timeout=60):
        yield app
