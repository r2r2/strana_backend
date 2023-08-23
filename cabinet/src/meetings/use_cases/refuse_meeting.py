import datetime
from asyncio import Task
from enum import IntEnum
from http import HTTPStatus
from typing import Any, Type

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoElementTypes, AmoTaskTypes
from common.email import EmailService
from fastapi import HTTPException
from src.task_management.constants import MeetingsSlug
from src.amocrm.repos import AmocrmStatus, AmocrmStatusRepo
from src.booking.constants import BookingSubstages
from src.booking.repos import BookingRepo
from src.notifications.services import GetEmailTemplateService
from src.task_management.services import UpdateTaskInstanceStatusService
from src.users.constants import UserType
from src.users.repos import User, UserRepo

from ..constants import MeetingStatusChoice
from ..entities import BaseMeetingCase
from ..exceptions import MeetingAlreadyFinishError, MeetingNotFoundError
from ..repos import Meeting, MeetingRepo, MeetingStatusRepo


class LeadStatuses(IntEnum):
    """
     Статусы закрытых сделок в амо.
    """
    UNREALIZED: int = 143  # Закрыто и не реализовано


class RefuseMeetingCase(BaseMeetingCase):
    """
    Кейс отмены встречи:
    """

    meeting_refused_to_client_mail = "meeting_refused_to_client_mail"
    meeting_refused_to_broker_mail = "meeting_refused_to_broker_mail"
    CLIENT_TASK_MESSAGE = 'Клиент отменил встречу.' \
                   'Необходимо связаться с клиентом для уточнения деталей.'
    BROKER_TASK_MESSAGE = 'Брокер отменил встречу.' \
                          'Необходимо связаться с клиентом для уточнения деталей.'

    def __init__(
        self,
        meeting_repo: Type[MeetingRepo],
        meeting_status_repo: Type[MeetingStatusRepo],
        user_repo: Type[UserRepo],
        booking_repo: Type[BookingRepo],
        amocrm_class: Type[AmoCRM],
        amocrm_status_repo: Type[AmocrmStatusRepo],
        email_class: Type[EmailService],
        get_email_template_service: GetEmailTemplateService,
        update_task_instance_status_service: UpdateTaskInstanceStatusService,
    ) -> None:
        self.meeting_repo: MeetingRepo = meeting_repo()
        self.meeting_status_repo: MeetingStatusRepo = meeting_status_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.user_repo: UserRepo = user_repo()
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.email_class: Type[EmailService] = email_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.update_task_instance_status_service: UpdateTaskInstanceStatusService = update_task_instance_status_service

    async def __call__(
        self,
        meeting_id: int,
        user_id: int,
    ) -> Meeting:
        meeting: Meeting = await self.meeting_repo.retrieve(
            filters=dict(id=meeting_id),
            related_fields=["booking", "project", "status"],
        )
        if not meeting:
            raise MeetingNotFoundError
        if meeting.status.slug in [MeetingStatusChoice.FINISH, MeetingStatusChoice.CANCELLED]:
            raise MeetingAlreadyFinishError

        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        if (user.type == UserType.CLIENT and meeting.booking.user_id != user.id) or (
                user.type in [UserType.AGENT, UserType.REPRES] and meeting.booking.agent_id != user.id
        ):
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.type in [UserType.AGENT, UserType.REPRES]:
            amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
                filters=dict(
                    pipeline_id=meeting.project.amo_pipeline_id,
                    name__icontains="фиксация клиента за ан",
                )
            )
            amocrm_status_id = amocrm_status.id
            amocrm_substage = BookingSubstages.MAKE_APPOINTMENT
        else:
            amocrm_status_id = LeadStatuses.UNREALIZED
            amocrm_substage = BookingSubstages.UNREALIZED

        # меняем статус сделки встречи
        booking_data: dict = dict(
            amocrm_status_id=amocrm_status_id,
            amocrm_substage=amocrm_substage,
        )
        await self.booking_repo.update(model=meeting.booking, data=booking_data)

        # завершаем встречу
        refused_meeting_status = await self.meeting_status_repo.retrieve(
            filters=dict(slug=MeetingStatusChoice.CANCELLED)
        )
        refused_meeting: Meeting = await self.meeting_repo.update(
            model=meeting,
            data=dict(status_id=refused_meeting_status.id),
        )
        prefetch_fields: list[str] = [
            "project",
            "project__city",
            "city",
            "booking",
            "booking__agent",
            "booking__agency",
            "booking__property",
        ]
        await refused_meeting.fetch_related(*prefetch_fields)

        async with await self.amocrm_class() as amocrm:
            lead_options: dict[str, Any] = dict(
                lead_id=meeting.booking.amocrm_id,
                status_id=amocrm_status_id,
            )
            await amocrm.update_lead_v4(**lead_options)

            complete_till_datetime = datetime.datetime.now() + datetime.timedelta(days=2)
            if user.type in [UserType.AGENT, UserType.REPRES]:
                responsible_user_id = user.amocrm_id
                text = self.BROKER_TASK_MESSAGE
            else:
                responsible_user_id = refused_meeting.booking.agent.amocrm_id if refused_meeting.booking.agent else None
                text = self.CLIENT_TASK_MESSAGE

            if responsible_user_id:
                await amocrm.create_task(
                    element_id=refused_meeting.booking.amocrm_id,
                    element_type=AmoElementTypes.CONTACT,
                    task_type=AmoTaskTypes.MEETING,
                    text=text,
                    complete_till=int(complete_till_datetime.timestamp()),
                    responsible_user_id=responsible_user_id
                )

        if user.type in [UserType.AGENT, UserType.REPRES]:
            await self.update_task_instance_status_service(
                booking_id=refused_meeting.booking_id,
                status_slug=MeetingsSlug.CANCELED.value,
            )
        elif refused_meeting.booking.agent:
            await self.update_task_instance_status_service(
                booking_id=refused_meeting.booking_id,
                status_slug=MeetingsSlug.CLIENT_CANCELED.value,
            )
            await self.send_email_to_broker(
                meeting=refused_meeting,
                user=user,
            )

        await self.send_email_to_client(
            meeting=refused_meeting,
            user=user,
        )

        return refused_meeting

    async def send_email_to_broker(
        self,
        meeting: Meeting,
        user: User,
    ) -> Task:
        """
        Уведомляем брокера о том, что встреча отменена.
        @param meeting: Meeting
        @param user: User
        @return: Task
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.meeting_refused_to_broker_mail,
            context=dict(meeting=meeting, user=user),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[user.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: EmailService = self.email_class(**email_options)

            return email_service.as_task()

    async def send_email_to_client(
        self,
        meeting: Meeting,
        user: User,
    ) -> Task:
        """
        Уведомляем клиента о том, что встреча отменена.
        @param meeting: Meeting
        @param user: User
        @return: Task
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.meeting_refused_to_client_mail,
            context=dict(meeting=meeting, user=user),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[user.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: EmailService = self.email_class(**email_options)

            return email_service.as_task()
