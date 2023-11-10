from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Path, Depends

from common import dependencies
from common.depreg import DepregAPI
from common.messages import SmsService
from config import site_config
from src.events_list.models import EventListQRCodeResponse
from src.events_list.repos import EventParticipantListRepo, EventListRepo, EventGroupRepo
from src.events_list.use_cases import EventParticipantListCase
from src.events_list.use_cases.event_list_qr_code_case import EventListQRCodeCase
from src.notifications.repos import QRcodeSMSNotifyRepo
from src.notifications.services import SendQRCodeSMS
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
        event_group_repo=EventGroupRepo,
        depreg_api=DepregAPI,
    )
    event_participant_list_case: EventParticipantListCase = EventParticipantListCase(**resources)
    await event_participant_list_case(event_id=event_id)


@router.post(
    "/{event_id}/send_sms/{notification_id}",
    status_code=HTTPStatus.OK,
)
async def send_sms_from_admin(
    event_id: int = Path(...),
    notification_id: int = Path(...),
):
    """
    Апи отправки смс из админки.
    """
    resources: dict[str, Any] = dict(
        event_list_repo=EventListRepo,
        qrcode_sms_notify_repo=QRcodeSMSNotifyRepo,
        event_participant_repo=EventParticipantListRepo,
        sms_class=SmsService,
        site_config=site_config,
    )
    send_qrcode_sms: SendQRCodeSMS = SendQRCodeSMS(**resources)
    data: dict[str, Any] = dict(event_id=event_id, notification_id=notification_id)
    await send_qrcode_sms(data=data)

