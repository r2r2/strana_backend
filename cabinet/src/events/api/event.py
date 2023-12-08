from datetime import datetime
from typing import Any, Optional

from common import dependencies, email
from fastapi import APIRouter, Body, Depends, Query, status, Path

from common.messages import SmsService
from src.agents import repos as agents_repos
from src.notifications import repos as notification_repos
from src.notifications import services as notification_services

from ..models import (RequestEventAdminModel, ResponseEventModel,
                      ResponseListEventModel)
from src.events.repos import (
    EventParticipantRepo,
    EventRepo,
)
from ..tasks import sending_sms_to_broker_on_event_task
from src.events.services import (
    EventNotificationTaskService,
    SendingSmsToBrokerOnEventService,
    GetEventNotificationTaskService,
)
from src.events.use_cases import (
    EventAgentRecordCase,
    EventAgentRefuseCase,
    EventDetailCase,
    EventListCase,
    EventSendEmailFromAdminCase,
    SendSMSFromAdminCase,
)
from src.users import repos as users_repos


router = APIRouter(prefix="/events", tags=["Events"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ResponseListEventModel,
)
async def event_list_view(
    show_only_recorded_meetings: bool = Query(
        default=False,
        description="Показывать только записанные встречи",
        alias="showOnlyRecordedMeetings",
    ),
    date_start: Optional[datetime] = Query(
        default=None,
        description="Дата начала фильтрации мероприятий для календаря",
        alias="dateStart",
    ),
    date_end: Optional[datetime] = Query(
        default=None,
        description="Дата конца фильтрации мероприятий для календаря",
        alias="dateEnd",
    ),
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
):
    """
    Апи списка мероприятий.
    """
    resources: dict[str, Any] = dict(
        event_repo=EventRepo,
        event_participant_repo=EventParticipantRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    event_list_case: EventListCase = EventListCase(**resources)
    return await event_list_case(
        show_only_recorded_meetings=show_only_recorded_meetings,
        user_id=user_id,
        date_start=date_start,
        date_end=date_end,
    )


@router.get(
    "/{event_id}",
    status_code=status.HTTP_200_OK,
    response_model=ResponseEventModel,
)
async def event_detail_view(
    event_id: int = Path(...),
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
):
    """
    Апи карточки мероприятия.
    """
    resources: dict[str, Any] = dict(
        event_repo=EventRepo,
        event_participant_repo=EventParticipantRepo,
        agent_repo=agents_repos.AgentRepo,
    )
    event_detail_case: EventDetailCase = EventDetailCase(**resources)
    return await event_detail_case(event_id=event_id, user_id=user_id)


@router.patch(
    "/{event_id}/accept",
    status_code=status.HTTP_200_OK,
    response_model=ResponseEventModel,
)
async def agent_record_on_event(
    event_id: int,
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
):
    """
    Апи записи на мероприятие.
    """
    get_event_sms_notification_service: GetEventNotificationTaskService = GetEventNotificationTaskService(
        event_sms_notification_repo=notification_repos.EventsSmsNotificationRepo,
    )
    event_notification_task_service: EventNotificationTaskService = EventNotificationTaskService(
        get_event_sms_notification_service=get_event_sms_notification_service,
        sending_sms_to_broker_on_event_task=sending_sms_to_broker_on_event_task,
    )
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        event_repo=EventRepo,
        event_participant_repo=EventParticipantRepo,
        agent_repo=agents_repos.AgentRepo,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
        event_notification_task_service=event_notification_task_service,
    )
    event_agent_record_case: EventAgentRecordCase = EventAgentRecordCase(**resources)
    return await event_agent_record_case(event_id=event_id, user_id=user_id)


@router.patch(
    "/{event_id}/refuse",
    status_code=status.HTTP_200_OK,
    response_model=ResponseEventModel,
)
async def agent_refuse_from_record(
    event_id: int,
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
):
    """
    Апи отказа от мероприятия.
    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        event_repo=EventRepo,
        event_participant_repo=EventParticipantRepo,
        agent_repo=agents_repos.AgentRepo,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
    )
    event_agent_refuse_case: EventAgentRefuseCase = EventAgentRefuseCase(**resources)
    return await event_agent_refuse_case(event_id=event_id, user_id=user_id)


@router.post(
    "/send_email_to_agent_from_admin",
    status_code=status.HTTP_200_OK,
)
async def send_email_to_agent(
    payload: RequestEventAdminModel = Body(...),
    data: str = Query(...),
):
    """
    Апи для отправки агенту письма при добавлении/удалении его к мероприятию админом.
    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    get_event_notification_task_service: GetEventNotificationTaskService = GetEventNotificationTaskService(
        event_sms_notification_repo=notification_repos.EventsSmsNotificationRepo,
        # sending_sms_to_broker_on_event_task=sending_sms_to_broker_on_event_task,
    )
    resources: dict[str, Any] = dict(
        event_repo=EventRepo,
        agent_repo=agents_repos.AgentRepo,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
        get_event_notification_template_service=get_event_notification_task_service,
    )
    send_email_to_agent_case: EventSendEmailFromAdminCase = EventSendEmailFromAdminCase(**resources)
    return await send_email_to_agent_case(payload=payload, data=data)


@router.post(
    "/{event_id}/send_sms_from_admin",
    status_code=status.HTTP_200_OK,
)
async def send_sms_from_admin(
    event_id: int = Path(...),
):
    """
    Апи для отправки смс из админки.
    """
    get_sms_template_service: notification_services.GetSmsTemplateService = notification_services.GetSmsTemplateService(
        sms_template_repo=notification_repos.SmsTemplateRepo,
    )
    resources: dict[str, Any] = dict(
        event_repo=EventRepo,
        event_participant_repo=EventParticipantRepo,
        user_repo=users_repos.UserRepo,
        sms_class=SmsService,
        get_sms_template_service=get_sms_template_service,
    )
    sending_sms_to_broker_on_event_service: SendingSmsToBrokerOnEventService = SendingSmsToBrokerOnEventService(
        **resources
    )
    resources: dict[str, Any] = dict(
        event_repo=EventRepo,
        event_sms_notification_repo=notification_repos.EventsSmsNotificationRepo,
        sending_sms_to_broker=sending_sms_to_broker_on_event_service,
    )
    send_sms: SendSMSFromAdminCase = SendSMSFromAdminCase(**resources)
    await send_sms(event_id=event_id)
