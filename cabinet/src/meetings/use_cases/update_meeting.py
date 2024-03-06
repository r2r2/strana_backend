from asyncio import Task
from datetime import timedelta, datetime
from http import HTTPStatus
from typing import Any

from fastapi import HTTPException

from common.amocrm import AmoCRM
from common.email import EmailService
from common.unleash.client import UnleashClient
from config.feature_flags import FeatureFlags
from src.users.repos import StranaOfficeAdminRepo
from src.amocrm.repos import AmocrmStatus, AmocrmStatusRepo
from src.booking.constants import BookingSubstages
from src.booking.repos import BookingRepo, Booking
from src.events.repos import CalendarEventRepo
from src.notifications.services import GetEmailTemplateService
from src.task_management.constants import MeetingsSlug
from src.task_management.services import UpdateTaskInstanceStatusService
from src.users.constants import UserType
from src.users.repos import User, UserRepo
from ..constants import MeetingStatusChoice, MeetingPropertyType, DEFAULT_RESPONSIBLE_USER_ID, MeetingType
from ..entities import BaseMeetingCase
from ..event_emitter_handlers import meeting_event_emitter
from ..exceptions import MeetingAlreadyFinishError, MeetingNotFoundError
from ..models import RequestUpdateMeetingModel
from ..repos import Meeting, MeetingRepo, MeetingStatusRepo, MeetingStatusRefRepo


class UpdateMeetingCase(BaseMeetingCase):
    """
    Кейс изменения встречи
    """
    meeting_updated_to_client_mail = "meeting_updated_to_client_mail"
    meeting_updated_to_broker_mail = "meeting_updated_to_broker_mail"
    meeting_updated_to_admin_mail = "meeting_updated_to_admin_mail"
    meeting_updated_to_admin_mail_client = "meeting_updated_to_admin_mail_client"
    amocrm_link = "https://eurobereg72.amocrm.ru/leads/detail/{id}"

    non_project_text = "не выбран"

    def __init__(
        self,
        meeting_repo: type[MeetingRepo],
        meeting_status_repo: type[MeetingStatusRepo],
        meeting_status_ref_repo: type[MeetingStatusRefRepo],
        calendar_event_repo: type[CalendarEventRepo],
        user_repo: type[UserRepo],
        booking_repo: type[BookingRepo],
        strana_office_admin_repo: type[StranaOfficeAdminRepo],
        amocrm_class: type[AmoCRM],
        amocrm_status_repo: type[AmocrmStatusRepo],
        email_class: type[EmailService],
        get_email_template_service: GetEmailTemplateService,
        update_task_instance_status_service: UpdateTaskInstanceStatusService,
    ) -> None:
        self.meeting_repo: MeetingRepo = meeting_repo()
        self.meeting_status_repo: MeetingStatusRepo = meeting_status_repo()
        self.meeting_status_ref_repo: MeetingStatusRefRepo = meeting_status_ref_repo()
        self.calendar_event_repo: CalendarEventRepo = calendar_event_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.strana_office_admin_repo: StranaOfficeAdminRepo = strana_office_admin_repo()
        self.user_repo: UserRepo = user_repo()
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.amocrm_class: type[AmoCRM] = amocrm_class
        self.email_class: type[EmailService] = email_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.update_task_instance_status_service: UpdateTaskInstanceStatusService = update_task_instance_status_service

    async def __call__(
        self,
        meeting_id: int,
        user_id: int,
        payload: RequestUpdateMeetingModel,
    ) -> Meeting:

        if self.__is_strana_lk_3011_add_enable:
            related_fields = ["status", "status_ref", "project", "city", "calendar_event", "booking"]
        elif self.__is_strana_lk_3011_use_enable:
            related_fields = ["status", "status_ref", "project", "city", "calendar_event", "booking"]
        elif self.__is_strana_lk_3011_off_old_enable:
            related_fields = ["status_ref", "project", "city", "calendar_event", "booking"]
        else:
            related_fields = ["status", "project", "city", "calendar_event", "booking"]

        meeting: Meeting = await self.meeting_repo.retrieve(
            filters=dict(id=meeting_id),
            related_fields=related_fields,
            prefetch_fields=[
                "project__city",
                "booking__user",
                "booking__agent",
                "booking__agency",
                "booking__property",
            ],
        )
        if not meeting:
            raise MeetingNotFoundError
        if self.__is_strana_lk_3011_add_enable:
            if meeting.status.slug in [MeetingStatusChoice.FINISH, MeetingStatusChoice.CANCELLED]:
                raise MeetingAlreadyFinishError
        elif self.__is_strana_lk_3011_use_enable:
            if meeting.status_ref_id in [MeetingStatusChoice.FINISH, MeetingStatusChoice.CANCELLED]:
                raise MeetingAlreadyFinishError
        elif self.__is_strana_lk_3011_off_old_enable:
            if meeting.status_ref_id in [MeetingStatusChoice.FINISH, MeetingStatusChoice.CANCELLED]:
                raise MeetingAlreadyFinishError
        else:
            if meeting.status.slug in [MeetingStatusChoice.FINISH, MeetingStatusChoice.CANCELLED]:
                raise MeetingAlreadyFinishError

        meeting_date_before = meeting.date.strftime("%Y-%m-%d %H:%M:%S")

        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        if (user.type == UserType.CLIENT and meeting.booking.user_id != user.id) or (
            user.type in [UserType.AGENT, UserType.REPRES] and meeting.booking.agent_id != user.id
        ):
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if self.__is_strana_lk_3011_add_enable:
            update_meeting: Meeting = await self._update_meeting(meeting, payload.date)
        elif self.__is_strana_lk_3011_use_enable:
            update_meeting: Meeting = await self._update_meeting_ref(meeting, payload.date)
        elif self.__is_strana_lk_3011_off_old_enable:
            update_meeting: Meeting = await self._update_meeting_ref(meeting, payload.date)
        else:
            update_meeting: Meeting = await self._update_meeting(meeting, payload.date)

        prefetch_fields: list[str] = [
            "project__city",
            "booking__user",
            "booking__agent",
            "booking__agency",
            "booking__property",
        ]
        await update_meeting.fetch_related(*prefetch_fields)

        # обновляем связанное событие календаря со встречей
        calendar_event_data = dict(date_start=update_meeting.date)
        await self.calendar_event_repo.update(model=update_meeting.calendar_event, data=calendar_event_data)

        if meeting.project:
            amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
                filters=dict(
                    pipeline_id=meeting.project.amo_pipeline_id,
                    name__icontains="Назначить встречу",
                )
            )
            new_responsible_user_id = None
        else:
            new_responsible_user_id = DEFAULT_RESPONSIBLE_USER_ID
            amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
                filters=dict(
                    pipeline_id=self.amocrm_class.PipelineIds.CALL_CENTER,
                    name__icontains="Назначен Zoom",
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
            if new_responsible_user_id:
                lead_options["project_amocrm_responsible_user_id"] = new_responsible_user_id
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
            await self.send_email(
                recipients=[user],
                context=dict(meeting=update_meeting, user=user),
                mail_event_slug=self.meeting_updated_to_broker_mail,
            )

            filters = dict(projects=update_meeting.project.id, type=update_meeting.type)
            admins = await self.strana_office_admin_repo.list(filters=filters)

            await self.send_email(
                recipients=admins,
                context=dict(
                    agent_fio=user.full_name,
                    meeting_date_before=meeting_date_before,
                    meeting_date_after=update_meeting.date.strftime("%Y-%m-%d %H:%M:%S"),
                    agent_phone=user.phone,
                    client_phone=update_meeting.booking.user.phone,
                    booking_link=self.amocrm_link.format(id=update_meeting.booking.amocrm_id),
                    city=update_meeting.city.name,
                    project=update_meeting.project.name,
                    property_type=MeetingPropertyType().to_label(update_meeting.property_type),
                ),
                mail_event_slug=self.meeting_updated_to_admin_mail,
            )

            await self.send_email(
                recipients=[update_meeting.booking.user],
                context=dict(meeting=update_meeting, user=user),
                mail_event_slug=self.meeting_updated_to_client_mail,
            )

        elif user.type == UserType.CLIENT:
            await self.update_task_instance_status_service(
                booking_id=update_meeting.booking_id,
                status_slug=MeetingsSlug.CLIENT_RESCHEDULED.value,
            )
            if update_meeting.booking.agent:
                await self.send_email(
                    recipients=[update_meeting.booking.agent],
                    context=dict(meeting=update_meeting, user=user),
                    mail_event_slug=self.meeting_updated_to_broker_mail,
                )

            if update_meeting.project:
                filters = dict(projects=update_meeting.project.id, type=update_meeting.type)
                project_name = update_meeting.project.name
            else:
                filters = dict(projects__city=update_meeting.city, type=MeetingType.ONLINE)
                project_name = self.non_project_text

            admins = list(set(await self.strana_office_admin_repo.list(filters=filters)))

            await self.send_email(
                recipients=admins,
                context=dict(
                    client_fio=user.full_name,
                    meeting_date_before=meeting_date_before,
                    meeting_date_after=update_meeting.date.strftime("%Y-%m-%d %H:%M:%S"),
                    agent_phone=update_meeting.booking.agent.phone if update_meeting.booking.agent else None,
                    client_phone=user.phone,
                    booking_link=self.amocrm_link.format(id=update_meeting.booking.amocrm_id),
                    city=update_meeting.city.name,
                    project=project_name,
                    property_type=MeetingPropertyType().to_label(update_meeting.property_type),
                ),
                mail_event_slug=self.meeting_updated_to_admin_mail_client,
            )

            await self.send_email(
                recipients=[user],
                context=dict(meeting=update_meeting, user=user),
                mail_event_slug=self.meeting_updated_to_client_mail,
            )

        return update_meeting

    async def send_email(
        self,
        recipients: list[User],
        context: dict,
        mail_event_slug: str,
    ) -> Task:
        """
        Уведомляем клиента о том, что встреча создана.
        @param recipients: User
        @param context: dict который вставляем в темплейт тела письма
        @param mail_event_slug: slug темплейта письма
        @return: Task
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=mail_event_slug,
            context=context,
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[recipient.email for recipient in recipients],
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

    async def _update_meeting(self, meeting, date) -> Meeting:
        old_status = meeting.status if meeting and meeting.status else None
        updated_meeting_status = await self.meeting_status_repo.retrieve(
            filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
        )
        update_data = dict(status_id=updated_meeting_status.id, date=date)
        update_meeting: Meeting = await self.meeting_repo.update(model=meeting, data=update_data)

        meeting_event_emitter.ee.emit(
            'meeting_status_changed',
            booking=meeting.booking,
            new_status=updated_meeting_status,
            old_status=old_status,
        )

        return update_meeting

    async def _update_meeting_ref(self, meeting, date) -> Meeting:
        old_status = meeting.status if meeting and meeting.status else None
        updated_meeting_status = await self.meeting_status_ref_repo.retrieve(
            filters=dict(slug=MeetingStatusChoice.NOT_CONFIRM)
        )
        update_data = dict(status_ref_id=updated_meeting_status.slug, date=date)

        update_meeting: Meeting = await self.meeting_repo.update(model=meeting, data=update_data)

        meeting_event_emitter.ee.emit(
            'meeting_status_changed',
            booking=meeting.booking,
            new_status=updated_meeting_status,
            old_status=old_status,
        )

        return update_meeting

    @property
    def __is_strana_lk_3011_add_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_add)

    @property
    def __is_strana_lk_3011_use_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_use)

    @property
    def __is_strana_lk_3011_off_old_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_off_old)
