from datetime import datetime, timedelta
from importlib import import_module

import pytest
from pytz import UTC

from src.events_list.repos import EventListRepo, EventParticipantListRepo


@pytest.fixture(scope="function")
def event_list_repo() -> EventListRepo:
    event_list_repo: EventListRepo = getattr(
        import_module("src.events_list.repos"), "EventListRepo"
    )()
    return event_list_repo


@pytest.fixture(scope="function")
def event_participant_list_repo() -> EventParticipantListRepo:
    event_participant_list_repo: EventParticipantListRepo = getattr(
        import_module("src.events_list.repos"), "EventParticipantListRepo"
    )()
    return event_participant_list_repo


@pytest.fixture(scope="function")
async def event_list(event_list_repo):
    today_date: datetime = datetime.now(tz=UTC)
    start_showing_date: datetime = today_date - timedelta(days=1)
    event_list = await event_list_repo.create(
        data=dict(
            name="Test event",
            token="test_token",
            event_date=today_date.strftime("%Y-%m-%d"),
            title="Test title",
            subtitle="Test subtitle",
            event_id=1,
            start_showing_date=start_showing_date.strftime("%Y-%m-%d"),
        )
    )
    return event_list


@pytest.fixture(scope="function")
async def event_participant_list(event_participant_list_repo, event_list, user):
    event_participant_list = await event_participant_list_repo.create(
        data=dict(
            phone=user.phone,
            code="test_code",
            event=event_list,
            group_id=1,
            timeslot="14:00",
        )
    )
    return event_participant_list
