from asyncio import Task
from http import HTTPStatus
from typing import Any, Type
from datetime import timedelta, datetime

from common.amocrm import AmoCRM
from common.email import EmailService
from fastapi import HTTPException

from src.task_management.constants import MeetingsSlug
from src.amocrm.repos import AmocrmStatus, AmocrmStatusRepo
from src.booking.constants import BookingSubstages
from src.booking.repos import BookingRepo
from src.events.repos import CalendarEventRepo
from src.notifications.services import GetEmailTemplateService
from src.task_management.services import UpdateTaskInstanceStatusService
from src.users.constants import UserType
from src.users.repos import User, UserRepo

from ..constants import MeetingStatusChoice
from ..entities import BaseMeetingCase
from ..exceptions import MeetingAlreadyFinishError, MeetingNotFoundError
from ..models import RequestUpdateMeetingModel
from ..repos import Meeting, MeetingRepo, MeetingStatusRepo


class UpdateMeetingCase(BaseMeetingCase):
    """
    Кейс изменения встречи
    """
    meeting_updated_to_client_mail = "meeting_updated_to_client_mail"
    meeting_updated_to_broker_mail = "meeting_updated_to_broker_mail"

    def __init__(
        self,
        meeting_repo: Type[MeetingRepo],
        meeting_status_repo: Type[MeetingStatusRepo],
        calendar_event_repo: Type[CalendarEventRepo],
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
        self.calendar_event_repo: CalendarEventRepo = calendar_event_repo()
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
        payload: RequestUpdateMeetingModel,
    ) -> Meeting:
        meeting: Meeting = await self.meeting_repo.retrieve(
            filters=dict(id=meeting_id),
            related_fields=[
                "status",
                "project",
                "project__city",
                "city",
                "calendar_event",
                "booking",
                "booking__user",
                "booking__agent",
                "booking__agency",
                "booking__property",
            ],
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

        updated_meeting_status = await self.meeting_status_repo.retrieve(
            filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
        )
        update_data = dict(statu_id=updated_meeting_status.id, date=payload.date)
        update_meeting: Meeting = await self.meeting_repo.update(model=meeting, data=update_data)

        # обновляем связанное событие календаря со встречей
        calendar_event_data = dict(date_start=update_meeting.date)
        await self.calendar_event_repo.update(model=update_meeting.calendar_event, data=calendar_event_data)

        amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
            filters=dict(
                pipeline_id=meeting.project.amo_pipeline_id,
                name__icontains="Назначить встречу",
            )
        )
        booking_data: dict = dict(
            amocrm_status_id=amocrm_status.id,
            amocrm_substage=BookingSubstages.MAKE_APPOINTMENT,
        )
        await self.booking_repo.update(model=meeting.booking, data=booking_data)

        async with await self.amocrm_class() as amocrm:
            amo_date: float = self.amo_date_formatter(update_meeting.date)
            lead_options: dict[str, Any] = dict(
                lead_id=meeting.booking.amocrm_id,
                status_id=amocrm_status.id,
                meeting_date_sensei=amo_date,
                meeting_date_zoom=amo_date,
                meeting_date_next_contact=amo_date,
            )
            await amocrm.update_lead_v4(**lead_options)

            amo_notes: str = f"Новое время встречи: {update_meeting.date.strftime('%Y-%m-%d %H:%M')}"
            await amocrm.send_lead_note(
                lead_id=update_meeting.booking.amocrm_id,
                message=amo_notes,
            )

        if user.type in [UserType.AGENT, UserType.REPRES]:
            await self.update_task_instance_status_service(
                booking_id=update_meeting.booking_id,
                status_slug=MeetingsSlug.RESCHEDULED.value,
            )
            await self.send_email_to_broker(
                meeting=update_meeting,
                user=user,
            )
        elif user.type == UserType.CLIENT:
            await self.update_task_instance_status_service(
                booking_id=update_meeting.booking_id,
                status_slug=MeetingsSlug.CLIENT_RESCHEDULED.value,
            )
            if update_meeting.booking.agent:
                await self.send_email_to_broker(
                    meeting=update_meeting,
                    user=user,
                )

        await self.send_email_to_client(
            meeting=update_meeting,
            user=update_meeting.booking.user,
        )

        return update_meeting

    async def send_email_to_broker(
        self,
        meeting: Meeting,
        user: User,
    ) -> Task:
        """
        Уведомляем брокера о том, что встреча изменена.
        @param meeting: Meeting
        @param user: User
        @return: Task
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.meeting_updated_to_broker_mail,
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
        Уведомляем клиента о том, что встреча изменена.
        @param meeting: Meeting
        @param user: User
        @return: Task
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.meeting_updated_to_client_mail,
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

    def amo_date_formatter(self, date: datetime) -> float:
        """
        Форматирование datetime для Амо
        """
        # Амо почему-то накидывает +2 часа
        amo_date_diff: datetime = date.replace(tzinfo=None) - timedelta(hours=2)
        amo_date_timestamp: float = amo_date_diff.timestamp()
        return amo_date_timestamp
