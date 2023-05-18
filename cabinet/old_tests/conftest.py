import asyncio
import io
import asyncio

import psycopg2

from PIL import Image
from faker import Faker
from pytest import fixture
from httpx import AsyncClient
from importlib import import_module
from unittest.mock import MagicMock
from pytest_mock import MockFixture
from tortoise.contrib.test import finalizer as finalize_database
from tortoise.contrib.test import initializer as initialize_database

from .booking.async_fixtures import *
from .booking.sync_fixtures import *
from .buildings.async_fixtures import *
from .buildings.sync_fixtures import *
from .common.async_fixtures import *
from .common.sync_fixtures import *
from .documents.async_fixtures import *
from .documents.sync_fixtures import *
from .floors.async_fixtures import *
from .floors.sync_fixtures import *
from .projects.sync_fixtures import *
from .properties.async_fixtures import *
from .properties.sync_fixtures import *
from .users.async_fixtures import *
from .users.sync_fixtures import *
from .tips.sync_fixtures import *
from .tips.async_fixtures import *
from .agencies.sync_fixtures import *
from .agencies.async_fixtures import *
from .agents.sync_fixtures import *
from .agents.async_fixtures import *
from .represes.sync_fixtures import *
from .represes.async_fixtures import *
from .pages.sync_fixtures import *
from .pages.async_fixtures import *
from .notifications.async_fixtures import *
from .notifications.sync_fixtures import *
from .admins.sync_fixtures import *
from .admins.async_fixtures import *
from .showtimes.async_fixtures import *
from .showtimes.sync_fixtures import *


@fixture(scope="function")
def async_mock():
    class AsyncMock(MagicMock):
        def __init__(self, call_return, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.call_return = call_return

        async def __call__(self, *args, **kwargs):
            return self.call_return

    return AsyncMock


@fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    return asyncio.get_event_loop()


@fixture(scope="session")
def initialize_application():
    initialize_application = getattr(import_module("config.initializers"), "initialize_application")
    return initialize_application


@fixture(scope="session")
def initialize_routers():
    initialize_routers = getattr(import_module("config.initializers"), "initialize_routers")
    return initialize_routers


@fixture(scope="session")
def initialize_exceptions():
    initialize_exceptions = getattr(import_module("config.initializers"), "initialize_exceptions")
    return initialize_exceptions


@fixture(scope="session")
def initialize_middlewares():
    initialize_middlewares = getattr(import_module("config.initializers"), "initialize_middlewares")
    return initialize_middlewares


@fixture(scope="session")
def database_modules():
    return getattr(import_module("config"), "tortoise_test_config")["apps"]["models"]["models"]


@fixture(scope="session")
def database_url(worker_id):
    from config import database_config

    database_url = database_config["test_dsn"].format(**database_config)

    db_elements = database_url.split("/")
    db_info = db_elements[-1]
    db_components = db_info.split("?")
    db_components[0] = db_components[0] + "_" + str(worker_id)
    db_elements[-1] = "?".join(db_components)
    database_url = "/".join(db_elements)
    return database_url


@fixture(scope="function")
def backend_config():
    backend_config = getattr(import_module("config"), "backend_config")
    return backend_config


@fixture(scope="function")
def sberbank_config():
    sberbank_config = getattr(import_module("config"), "sberbank_config")
    return sberbank_config


@fixture(scope="function")
def amocrm_config():
    amocrm_config = getattr(import_module("config"), "amocrm_config")
    return amocrm_config


@fixture(scope="function")
def image_factory():
    def get_image(image_name):
        file = io.BytesIO()
        image = Image.new("RGBA", size=(100, 100), color=(155, 0, 0))
        image.save(file, "png")
        file.name = image_name
        file.seek(0)
        return file

    return get_image


@fixture(scope="function")
def faker():
    faker = Faker("ru_RU")
    return faker


@fixture(scope="session")
def application(
    initialize_application,
    initialize_middlewares,
    initialize_exceptions,
    initialize_routers,
    database_modules,
    database_url,
    redis,
):
    application = initialize_application()
    initialize_middlewares(application)
    initialize_routers(application)
    initialize_exceptions(application)
    initialize_database(database_modules, db_url=database_url)
    yield application

    finalize_database()


@fixture(scope="session")
async def redis():
    redis = getattr(import_module("common.redis"), "broker")
    await redis.connect()
    yield redis
    await redis.flush()
    await redis.disconnect()


@fixture(scope="function")
async def client(application):
    async with AsyncClient(app=application, base_url="http://localhost") as client:
        yield client


@fixture(scope="function")
async def client_with_session_cookie(application):
    async with AsyncClient(
        app=application,
        base_url="http://localhost",
        cookies={"_lksession": ("pikachu_test" * 8)[:86]},
    ) as client:
        yield client


@fixture(scope="function", autouse=True)
def clear_database_tables(database_url: str) -> None:
    """Очищаем все таблицы в тестовой БД."""
    yield
    conn = psycopg2.connect(database_url.rsplit("?")[0])

    table_names = get_all_db_table_names(conn)
    truncate_query = "TRUNCATE {} RESTART IDENTITY".format(",".join(table_names))

    cur = conn.cursor()
    cur.execute(truncate_query)
    conn.commit()

    cur.close()
    conn.close()


def get_all_db_table_names(conn) -> set[str]:
    """Достаём все таблицы приложения."""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        AND table_type='BASE TABLE';
        """
    )
    table_names: list[tuple[str]] = cur.fetchall()
    cur.close()
    return set(table_name[0] for table_name in table_names)


@fixture(scope="function", autouse=True)
async def sent_emails():
    """Плохой код для получения списка отправленных email-ов.

    В будущем EmailService стоит отрефакторить на моковый сервис.
    """
    from fastapi_mail import FastMail

    sent_messages = []

    async def mock_send_message(self, message) -> None:
        sent_messages.append(message)

    FastMail.send_message = mock_send_message
    yield sent_messages
    sent_messages.clear()
