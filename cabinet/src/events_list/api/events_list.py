from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Path

from common.depreg import DepregAPI
from src.events_list.repos import EventParticipantListRepo, EventListRepo
from src.events_list.use_cases import EventParticipantListCase


router = APIRouter(prefix="/events_list", tags=["Список мероприятий"])


@router.patch(
    "/{event_id}/update_event_participant_list/",
    status_code=HTTPStatus.OK,
)
async def update_event_participant_list(
    event_id: int = Path(...),
) -> None:
    """
    Апи обновления списка участников мероприятия.
    """
    resources: dict[str, Any] = dict(
        event_list_repo=EventListRepo,
        event_participant_list_repo=EventParticipantListRepo,
        depreg_api=DepregAPI,
    )
    event_participant_list_case: EventParticipantListCase = EventParticipantListCase(**resources)
    await event_participant_list_case(event_id=event_id)
