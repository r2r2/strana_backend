from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Path, Depends

from common import dependencies
from common.depreg import DepregAPI
from src.events_list.models import EventListQRCodeResponse
from src.events_list.repos import EventParticipantListRepo, EventListRepo
from src.events_list.use_cases import EventParticipantListCase
from src.events_list.use_cases.event_list_qr_code_case import EventListQRCodeCase
from src.users import repos as user_repos


router = APIRouter(prefix="/events_list", tags=["Список мероприятий"])


@router.get(
    "/qr_code/",
    status_code=HTTPStatus.OK,
    response_model=EventListQRCodeResponse | None,
)
async def get_qr_code(
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
):
    """
    Апи получения QR-кода.
    """
    resources: dict[str, Any] = dict(
        event_list_repo=EventListRepo,
        user_repo=user_repos.UserRepo,
        event_participant_list_repo=EventParticipantListRepo,
    )
    event_list_qr_code: EventListQRCodeCase = EventListQRCodeCase(**resources)
    return await event_list_qr_code(user_id=user_id)


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
