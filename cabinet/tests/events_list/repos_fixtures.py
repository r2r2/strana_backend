from importlib import import_module

import pytest

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
