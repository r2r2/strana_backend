import pytest
from importlib import import_module

from src.meetings.repos import MeetingRepo


@pytest.fixture(scope="function")
def meeting_repo() -> MeetingRepo:
    meeting_repo: MeetingRepo = getattr(import_module("src.meetings.repos"), "MeetingRepo")()
    return meeting_repo


@pytest.fixture(scope="function")
async def meeting_fixture() -> MeetingRepo:
    from datetime import datetime
    meeting_repo: MeetingRepo = getattr(import_module("src.meetings.repos"), "MeetingRepo")()
    meeting_data: dict = dict(
        date=datetime.now(),
        status="not_confirm",
    )
    meeting = await meeting_repo.create(data=meeting_data)
    return meeting
