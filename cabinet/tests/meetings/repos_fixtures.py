import pytest
from importlib import import_module

from src.meetings.repos import MeetingRepo, MeetingStatusRepo, MeetingStatus


@pytest.fixture(scope="function")
def meeting_repo() -> MeetingRepo:
    meeting_repo: MeetingRepo = getattr(import_module("src.meetings.repos"), "MeetingRepo")()
    return meeting_repo


@pytest.fixture(scope="function")
def meeting_status_repo() -> MeetingStatusRepo:
    meeting_status_repo: MeetingStatusRepo = getattr(import_module("src.meetings.repos"), "MeetingStatusRepo")()
    return meeting_status_repo


@pytest.fixture(scope="function")
async def meeting_status(meeting_status_repo) -> MeetingStatus:
    meeting_status: MeetingStatus = await meeting_status_repo.create(
        data=dict(
            sort=100,
            slug="not_confirm",
            label="Не подтверждено",
        )
    )
    return meeting_status


@pytest.fixture(scope="function")
async def meeting_fixture(meeting_status) -> MeetingRepo:
    from datetime import datetime
    meeting_repo: MeetingRepo = getattr(import_module("src.meetings.repos"), "MeetingRepo")()
    meeting_data: dict = dict(
        date=datetime.now(),
        status=meeting_status,
    )
    meeting = await meeting_repo.create(data=meeting_data)
    return meeting
