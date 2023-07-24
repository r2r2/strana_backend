import pytest
from importlib import import_module

from src.events.repos import EventRepo, Event


@pytest.fixture(scope="function")
def event_repo() -> EventRepo:
    event_repo: EventRepo = getattr(import_module("src.events.repos"), "EventRepo")()
    return event_repo


@pytest.fixture(scope="function")
async def event_fixture(event_repo, city) -> None:
    from datetime import datetime, timedelta
    from pytz import UTC
    event_data: dict = dict(
        name="Тестовое мероприятие 1",
        type="online",
        meeting_date_start=datetime.now(tz=UTC) + timedelta(hours=1),
        manager_fio="Тестовый ФИО",
        manager_phone="+79999999999",
        is_active="True",
    )
    await event_repo.create(data=event_data)
    event_data: dict = dict(
        name="Тестовое мероприятие 2",
        type="offline",
        meeting_date_start=datetime.now(tz=UTC) - timedelta(hours=1),
        manager_fio="Тестовый ФИО",
        manager_phone="+79999999999",
        is_active=True,
        show_in_all_cities=True,
    )
    await event_repo.create(data=event_data)
    event_data: dict = dict(
        name="Тестовое мероприятие 3",
        type="offline",
        city=city,
        meeting_date_start=datetime.now(tz=UTC) + timedelta(hours=1),
        manager_fio="Тестовый ФИО",
        manager_phone="+79999999999",
        is_active=True,
        show_in_all_cities=False,
    )
    await event_repo.create(data=event_data)
