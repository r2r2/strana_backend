import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from fastapi.testclient import TestClient

BASE_URL: str = "http://localhost:8080"


@pytest.fixture(scope="module")
def sync_client(application: FastAPI):
    """
    Синхронный клиент
    """
    sync_client: TestClient = TestClient(app=application, base_url=BASE_URL)
    yield sync_client


@pytest.fixture(scope="module")
async def async_client(application: FastAPI):
    """
    Асинхронный (пока не работает)
    """
    async with AsyncClient(app=application, base_url=BASE_URL) as async_client:
        yield async_client
