from typing import AsyncGenerator

import pytest
from async_asgi_testclient import TestClient as WSClient
from fastapi import FastAPI


@pytest.fixture(
    scope="function",
    name="ws_client",
)
async def ws_test_client_fixture(app_lifespan: FastAPI) -> AsyncGenerator[WSClient, None]:
    client = WSClient(app_lifespan)
    yield client


__all__ = (
    "WSClient",
    "ws_test_client_fixture",
)
