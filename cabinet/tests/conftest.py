"""
Импорт фикстур
"""
from unittest import mock
from pytest_mock import MockFixture

# основные фикстуры
from .event_loop_fixtures import *
from .db_fixtures import *
from .app_fixtures import *
from .client_fixtures import *
from .faker_fixtures import *
from .config.fixtures import *

# фикстуры приложений
from .common.sync_fixtures import *
from .users.repos_fixtures import *
from .users.sync_fixtures import *
from .users.async_fixtures import *
from .agencies.sync_fixtures import *
from .agencies.async_fixtures import *
from .agencies.repos_fixtures import *
from .properties.repos_fixtures import *
from .bookings.repos_fixtures import *
from .meetings.repos_fixtures import *
from .projects.repos_fixtures import *
from .cities.repos_fixtures import *
from .notifications.repos_fixtures import *
from .floors.repos_fixtures import *
from .buildings.repos_fixtures import *
from .agents.repos_fixtures import *
from .admins.repos_fixtures import *
from .represes.repos_fixtures import *
from .dashboard.repos_fixtures import *
from .events.repos_fixtures import *
from .documents.repos_fixtures import *
from .favourites.repos_fixtures import *
from .task_management.repos_fixtures import *
from .amocrm.repos_fixtures import *
from .additional_services.repos_fixtures import *
from .api_integrations.test_depreg import *
from .events_list.repos_fixtures import *
from .news.repos_fixtures import *
from .mortgage.repos_fixtures import *


@pytest.fixture
def mocker():
    """Fixture to provide the `mocker` object for mocking."""
    return mock.Mock()


@fixture(scope="session")
async def redis():
    redis = getattr(import_module("common.redis"), "broker")
    await redis.connect()
    yield redis
    await redis.disconnect()
