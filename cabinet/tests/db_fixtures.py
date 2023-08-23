import asyncio
import fcntl
import os
import subprocess
import tempfile
import threading
from datetime import datetime
from importlib import import_module
from multiprocessing import Lock
from typing import Any

import pytest
from tortoise import Tortoise
from tortoise.backends.asyncpg import AsyncpgDBClient

from config import tortoise_test_config as tortoise_config
from tortoise.contrib.test import initializer as initialize_database


@pytest.fixture(scope="session")
def database_url(
    database_config: dict[str, Any],
    test_credentials: dict[str, Any],
    db_name: str,
    test_db_user: str,
) -> str:
    # uri: str = database_config["test_dsn"].format(
    #     user=test_db_user,
    #     password=test_credentials['password'],
    #     host=test_credentials['host'],
    #     port=test_credentials['port'],
    #     database_test=db_name,
    #     maxsize=database_config['maxsize'],
    # )
    # return uri
    return f"postgres://strana_test:9q229o2972f2a8S@127.0.0.1:5433/cabinet_test?maxsize=20"


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
    # return dict(
    #     user=test_db_user,
    #     password=test_credentials['password'],
    #     host=test_credentials['host'],
    #     port=test_credentials['port'],
    #     database=database_config['database'],
    #     connection_name=connection_name,
    # )
    return dict(
                user="strana_test",
                password="9q229o2972f2a8S",
                host="127.0.0.1",
                port=5433,
                database="postgres",
                connection_name="cabinet",
            )


@pytest.fixture(scope="session")
def test_db_user(test_credentials) -> str:
    return test_credentials['user']


@pytest.fixture(scope="session")
def db_name(test_credentials) -> str:
    db_name: str = test_credentials['database']
    db_name += datetime.now().strftime('_%d_%m_%Y_%H_%M_%S')
    # return db_name
    return "cabinet_test"

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
    connection_creds: dict[str, Any],
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

############################################################################################################

# database_created = False
database_lock = Lock()
#
#
# @pytest.fixture(scope="session", autouse=True)
# async def database(
#     database_url: str,
#     database_modules: list[str],
#     db_name: str,
#     test_db_user: str,
#     connection_creds: dict[str, Any],
#     db_client: AsyncpgDBClient,
# ):
#     """
#     Test database setup and teardown.
#     """
#     global database_created
#
#     if not database_created:
#         with database_lock:
#             if not database_created:
#                 await db_client.create_connection(with_db=True)
#                 await db_client.execute_script(f'CREATE DATABASE {db_name} OWNER {test_db_user};')
#                 database_created = True
#
#     modules: dict = dict(models=database_modules)
#     await Tortoise.init(db_url=database_url, modules=modules)
#     print(f"Test database created! {database_url = }")
#     await Tortoise.generate_schemas()
#     print("Success to generate schemas!")
#
#     yield
#
#     await Tortoise.close_connections()
#
#
# def pytest_sessionfinish(session, exitstatus):
#     global database_created
#
#     if database_created:
#         with database_lock:
#             if database_created:
#                 loop = asyncio.get_event_loop()
#
#                 db_name = "cabinet_test"
#
#                 connection_creds = dict(
#                     user="strana_test",
#                     password="9q229o2972f2a8S",
#                     host="127.0.0.1",
#                     port=5433,
#                     database="postgres",
#                     connection_name="cabinet",
#                 )
#                 db_client = AsyncpgDBClient(**connection_creds)
#                 loop.run_until_complete(db_client.create_connection(with_db=True))
#
#                 # Drop the database
#                 loop.run_until_complete(db_client.execute_script(f'DROP DATABASE IF EXISTS {db_name};'))
#
#                 print("\nTest database dropped...")
#                 database_created = False
# @pytest.fixture(scope="session", autouse=True)
# async def database_setup_teardown(database_url, database_modules):
#     db_name = "cabinet_test"
#     db_user = "strana_test"
#     db_password = "9q229o2972f2a8S"
#
#     # Acquire the lock
#     with database_lock:
#         if not os.environ.get("DB_SETUP_DONE"):
#             pr = subprocess.run(
#                 ["python", "-m", "tests.manage_test_db", "create", "--db_name", db_name, "--db_user", db_user, "--db_password", db_password],
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#             )
#             print(f"{pr = }")
#             print(f'{pr.returncode=}')
#             print(f"{pr.stdout=}")
#             print(f"{pr.stderr=}")
#             modules: dict = dict(models=database_modules)
#             await Tortoise.init(db_url=database_url, modules=modules)
#             await Tortoise.generate_schemas()
#             os.environ["DB_SETUP_DONE"] = "True"  # Mark setup as done
#
#     yield
#
#     await Tortoise.close_connections()
#
#     # Teardown the database
#     with database_lock:
#         if os.environ.get("DB_SETUP_DONE"):
#             subprocess.run(
#                 ["python", "-m", "tests.manage_test_db", "drop", "--db_name", db_name, "--db_user", db_user, "--db_password", db_password],
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#             )
#             os.environ.pop("DB_SETUP_DONE", None)  # Remove setup flag


# Create a file-based lock
# lock_file_path = os.path.join(tempfile.gettempdir(), "database_lock.txt")
#
# @pytest.fixture(scope="session", autouse=True)
# async def database_setup_teardown(database_url, database_modules):
#     db_name = "cabinet_test"
#     db_user = "strana_test"
#     db_password = "9q229o2972f2a8S"
#
#     # Acquire the file-based lock
#     with open(lock_file_path, "w") as lock_file:
#         try:
#             fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)  # Acquire exclusive lock
#             pr = subprocess.run(
#                 ["python", "-m", "tests.manage_test_db", "create", "--db_name", db_name, "--db_user", db_user, "--db_password", db_password],
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#             )
#             print(f"{pr = }")
#             print(f'{pr.returncode=}')
#             print(f"{pr.stdout=}")
#             print(f"{pr.stderr=}")
#             modules: dict = dict(models=database_modules)
#             await Tortoise.init(db_url=database_url, modules=modules)
#             await Tortoise.generate_schemas()
#         except BlockingIOError:
#             print("Another process is already setting up the database. Skipping setup.")
#             # Skip database setup as it's being done by another process
#
#     yield
#
#     await Tortoise.close_connections()
#
#     # Release the file-based lock
#     with open(lock_file_path, "w") as lock_file:
#         fcntl.flock(lock_file, fcntl.LOCK_UN)  # Release the lock
#
#     # Teardown the database
#     if os.path.exists(lock_file_path):
#         subprocess.run(
#             ["python", "-m", "tests.manage_test_db", "drop", "--db_name", db_name, "--db_user", db_user, "--db_password", db_password],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#         )
#         os.remove(lock_file_path)  # Remove the lock file
# aerich_table_lock = Lock()
#
#
# @pytest.fixture(scope="session", autouse=True)
# async def database_setup_teardown(database_url, database_modules):
#     db_name = "cabinet_test"
#     db_user = "strana_test"
#     db_password = "9q229o2972f2a8S"
#
#     if os.environ.get("DB_SETUP_DONE") is None:
#         with database_lock:
#             if os.environ.get("DB_SETUP_DONE") is None:
#                 # Create the database
#                 create_database(
#                     db_name=db_name,
#                     db_user=db_user,
#                     db_password=db_password,
#                 )
#
#                 modules: dict = dict(models=database_modules)
#
#                 await Tortoise.init(db_url=database_url, modules=modules)
#                 aerich_table_lock.acquire()
#                 try:
#                     await Tortoise.generate_schemas()
#                 finally:
#                     aerich_table_lock.release()
#                 # await Tortoise.generate_schemas()
#                 os.environ["DB_SETUP_DONE"] = "True"
#
#
#     yield
#
#     # Teardown the database
#     with database_lock:
#         if os.environ.get("DB_SETUP_DONE") == "True":
#             drop_database(
#                 db_name=db_name,
#                 db_user=db_user,
#                 db_password=db_password,
#             )
#             os.environ.pop("DB_SETUP_DONE")
#
#
# def create_database(
#     db_name: str,
#     db_user: str,
#     db_password: str,
# ):
#     pr = subprocess.run(
#         ["python", "-m", "tests.manage_test_db", "create", "--db_name", db_name, "--db_user", db_user, "--db_password",
#          db_password],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#     )
#     # print(f"{pr = }")
#     print(f'{pr.returncode=}')
#     print(f"{pr.stdout=}")
#     print(f"{pr.stderr=}")
#
#
# def drop_database(
#     db_name: str,
#     db_user: str,
#     db_password: str,
# ):
#     subpr = subprocess.run(
#         ["python", "-m", "tests.manage_test_db", "drop", "--db_name", db_name, "--db_user", db_user, "--db_password",
#          db_password],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#     )
#     # print(f"{subpr = }")
#     print(f'{subpr.returncode=}')
#     print(f"{subpr.stdout=}")
#     print(f"{subpr.stderr=}")

