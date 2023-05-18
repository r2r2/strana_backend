from importlib import import_module

import pytest
from tortoise import Tortoise


TEST_DB_URL: str = "sqlite://test_db.sqlite3"


@pytest.fixture(scope="session")
def database_url(test_db_url: str = TEST_DB_URL) -> str:
    return test_db_url


@pytest.fixture(scope="session")
def database_modules() -> list[str]:
    return getattr(import_module("config"), "tortoise_test_config")["apps"]["models"]["models"]


@pytest.fixture(scope="session", autouse=True)
async def database(database_url: str, database_modules: list[str]):
    """
    Тестовая база данных
    """
    modules: dict = dict(models=database_modules)
    try:
        await Tortoise.init(db_url=database_url, modules=modules, _create_db=True)
        print(f"Test database created! {database_url = }")

        await Tortoise.generate_schemas()
        print("Success to generate schemas!")

        yield
    finally:
        await Tortoise._drop_databases()
        print("\nTest database dropped...")
