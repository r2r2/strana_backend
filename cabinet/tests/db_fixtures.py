from datetime import datetime
from importlib import import_module
from typing import Any

import pytest
from tortoise import Tortoise
from tortoise.backends.asyncpg import AsyncpgDBClient


@pytest.fixture(scope="session")
def database_url(
    database_config: dict[str, Any],
    test_credentials: dict[str, Any],
    db_name: str,
    test_db_user: str,
) -> str:
    uri: str = database_config["test_dsn"].format(
        user=test_db_user,
        password=test_credentials['password'],
        host=test_credentials['host'],
        port=test_credentials['port'],
        database_test=db_name,
        maxsize=database_config['maxsize'],
    )
    return uri


@pytest.fixture(scope="session")
def tortoise_test_config() -> dict[str, Any]:
    return getattr(import_module("config"), "tortoise_test_config")


@pytest.fixture(scope="session")
def database_config() -> dict[str, Any]:
    return getattr(import_module("config"), "database_config")


@pytest.fixture(scope="session")
def test_credentials(tortoise_test_config: dict[str, Any], connection_name: str) -> dict[str, Any]:
    credentials: dict[str, Any] = tortoise_test_config['connections'][connection_name]['credentials']
    return credentials


@pytest.fixture(scope="session")
def connection_name(tortoise_test_config: dict[str, Any]) -> str:
    return tortoise_test_config['apps']['models']['default_connection']


@pytest.fixture(scope="session")
def connection_creds(
    database_config: dict[str, Any],
    test_credentials: dict[str, Any],
    connection_name: str,
    test_db_user: str,
) -> dict[str, Any]:
    return dict(
        user=test_db_user,
        password=test_credentials['password'],
        host=test_credentials['host'],
        port=test_credentials['port'],
        database=database_config['database'],
        connection_name=connection_name,
    )


@pytest.fixture(scope="session")
def test_db_user(test_credentials) -> str:
    return test_credentials['user']


@pytest.fixture(scope="session")
def db_name(test_credentials) -> str:
    db_name: str = test_credentials['database']
    db_name += datetime.now().strftime('_%d_%m_%Y_%H_%M_%S')
    return db_name


@pytest.fixture(scope="session")
def database_modules() -> list[str]:
    return getattr(import_module("config"), "tortoise_test_config")["apps"]["models"]["models"]


@pytest.fixture(scope="session")
async def db_client(connection_creds):
    db_client = AsyncpgDBClient(**connection_creds)
    await db_client.create_connection(with_db=True)
    yield db_client
    await db_client.close()


@pytest.fixture(scope="session", autouse=True)
async def database(
    database_url: str,
    database_modules: list[str],
    db_name: str,
    test_db_user: str,
    db_client: AsyncpgDBClient,
):
    """
    Тестовая база данных
    """
    await db_client.create_connection(with_db=True)
    await db_client.execute_script(f'CREATE DATABASE {db_name} OWNER {test_db_user};')

    modules: dict = dict(models=database_modules)
    await Tortoise.init(db_url=database_url, modules=modules)
    print(f"Test database created! {database_url = }")
    await Tortoise.generate_schemas()
    print("Success to generate schemas!")

    yield

    await Tortoise.close_connections()
    await db_client.execute_script(f'DROP DATABASE IF EXISTS {db_name};')
