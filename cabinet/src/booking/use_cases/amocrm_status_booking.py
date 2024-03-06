from asyncio import Task
from typing import Any, Optional, Type, Union
from urllib.parse import parse_qs, unquote

import structlog
from fastapi import BackgroundTasks

from common.amocrm import AmoCRM
from common.amocrm.exceptions import AmoContactIncorrectPhoneFormatError
from common.amocrm.repos import AmoStatusesRepo
from common.backend.models.amocrm import AmocrmStatus
from common.email import EmailService
from common.sentry.utils import send_sentry_log
from common.unleash.client import UnleashClient
from common.utils import parse_phone
from config.feature_flags import FeatureFlags
from src.amocrm.repos import AmocrmStatusRepo
from src.events.repos import CalendarEventRepo
from src.meetings.constants import MeetingType, MeetingStatusChoice
from src.meetings.repos import MeetingRepo, Meeting, MeetingStatusRepo
from src.meetings.repos import MeetingStatusRefRepo
from src.meetings.services import CreateRoomService, ImportMeetingFromAmoService
from src.notifications.services import GetEmailTemplateService
from src.projects.repos import ProjectRepo
from src.task_management.constants import MeetingsSlug
from src.task_management.dto import CreateTaskDTO
from src.task_management.services import CreateTaskInstanceService, UpdateTaskInstanceStatusService
from src.task_management.utils import check_task_instance_exists
from src.users.constants import UserType
from src.users.repos import UserRepo, User
from src.users.services import ImportClientFromAmoService
from ..constants import BookingStagesMapping, BookingSubstages
from ..loggers.wrappers import booking_changes_logger
from ..repos import Booking, BookingRepo, WebhookRequestRepo
from ..services import BookingCreationFromAmoService
from ..tasks import send_sms_to_msk_client_task
from ..types import (
    BookingAmoCRM, BookingPropertyRepo, BookingRequest, CustomFieldValue, WebhookLead
)
from src.meetings.event_emitter_handlers import meeting_event_emitter

MEETING_STATUSES = [
    AmoCRM.TMNStatuses.MAKE_APPOINTMENT,
    AmoCRM.TMNStatuses.ASSIGN_AGENT,
    AmoCRM.TMNStatuses.MEETING,
    AmoCRM.TMNStatuses.MEETING_IN_PROGRESS,

    AmoCRM.MSKStatuses.MAKE_APPOINTMENT,
    AmoCRM.MSKStatuses.ASSIGN_AGENT,
    AmoCRM.MSKStatuses.MEETING,
    AmoCRM.MSKStatuses.MEETING_IN_PROGRESS,

    AmoCRM.SPBStatuses.MAKE_APPOINTMENT,
    AmoCRM.SPBStatuses.ASSIGN_AGENT,
    AmoCRM.SPBStatuses.MEETING,
    AmoCRM.SPBStatuses.MEETING_IN_PROGRESS,

    AmoCRM.EKBStatuses.MAKE_APPOINTMENT,
    AmoCRM.EKBStatuses.ASSIGN_AGENT,
    AmoCRM.EKBStatuses.MEETING,
    AmoCRM.EKBStatuses.MEETING_IN_PROGRESS,
]


class AmoStatusBookingCase:
    amocrm_group_status_default_name: str = "Бронь"
    constraint_name: str = "users_user_unique_together_email_type"

    name_field_id: int = 812918
    surname_field_id: int = 812920
    patronymic_field_id: int = 812922

    meeting_change_status_to_client_mail: str = "meeting_change_status_to_client_mail"
    meeting_change_status_to_broker_mail: str = "meeting_change_status_to_broker_mail"

    def __init__(
            self,
            *,
            amocrm_config: dict[str, Any],
            backend_config: dict[str, Any],
            booking_repo: Type[BookingRepo],
            meeting_repo: Type[MeetingRepo],
            meeting_status_repo: Type[MeetingStatusRepo],
            meeting_status_ref_repo: Type[MeetingStatusRefRepo],
            calendar_event_repo: Type[CalendarEventRepo],
            user_repo: Type[UserRepo],
            project_repo: Type[ProjectRepo],
            amocrm_status_repo: Type[AmocrmStatusRepo],
            amocrm_class: Type[BookingAmoCRM],
            request_class: Type[BookingRequest],
            property_repo: Type[BookingPropertyRepo],
            webhook_request_repo: Type[WebhookRequestRepo],
            create_meeting_room_service: CreateRoomService,
            statuses_repo: Type[AmoStatusesRepo],
            background_tasks: BackgroundTasks,
            create_booking_log_task: Optional[Any] = None,
            create_task_instance_service: CreateTaskInstanceService,
            update_task_instance_service: UpdateTaskInstanceStatusService,
            email_class: Type[EmailService],
            get_email_template_service: GetEmailTemplateService,
            import_contact_service: ImportClientFromAmoService,
            import_meeting_service: ImportMeetingFromAmoService,
            booking_creation_service: BookingCreationFromAmoService,

            logger: Optional[Any] = structlog.getLogger(__name__),
    ) -> None:

        self.logger = logger
        self.booking_repo: BookingRepo = booking_repo()
        self.meeting_repo: MeetingRepo = meeting_repo()
        self.meeting_status_repo: MeetingStatusRepo = meeting_status_repo()
        self.meeting_status_ref_repo: MeetingStatusRefRepo = meeting_status_ref_repo()
        self.calendar_event_repo: CalendarEventRepo = calendar_event_repo()
        self.user_repo: UserRepo = user_repo()
        self.project_repo: ProjectRepo = project_repo()
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.property_repo: BookingPropertyRepo = property_repo()
        self.webhook_request_repo: WebhookRequestRepo = webhook_request_repo()
        self.statuses_repo: AmoStatusesRepo = statuses_repo()
        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.request_class: Type[BookingRequest] = request_class
        self.create_meeting_room_service: CreateRoomService = create_meeting_room_service
        self.background_tasks: BackgroundTasks = background_tasks
        self.create_task_instance_service: CreateTaskInstanceService = create_task_instance_service
        self.update_task_instance_service: UpdateTaskInstanceStatusService = update_task_instance_service
        self.email_class: Type[EmailService] = email_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.import_contact_service: ImportClientFromAmoService = import_contact_service
        self.import_meeting_service: ImportMeetingFromAmoService = import_meeting_service
        self.booking_creation_service: BookingCreationFromAmoService = booking_creation_service

        self.secret: str = amocrm_config["secret"]
        self.login: str = backend_config["internal_login"]
        self.password: str = backend_config["internal_password"]
        self.backend_url: str = backend_config["url"] + backend_config["graphql"]

        self.create_booking_log_task: Any = create_booking_log_task
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Изменение статуса webhook | AMOCRM"
        )
        self.booking_deactivate = booking_changes_logger(
            self.booking_repo.update, self, content="Деактивация брони webhook воронка не поддерживается | AMOCRM"
        )

    async def __call__(self, payload: bytes) -> None:
        data: dict[str, Any] = parse_qs(unquote(payload.decode("utf-8")))
        webhook_lead: WebhookLead = self._parse_data(data=data)
        booking_new_status = await self._get_booking_creation_status(webhook_lead)
        booking: Booking | None = await self._get_booking(webhook_lead)
        user: User = await self._get_user(webhook_lead)

        if booking is None and booking_new_status.name == self.amocrm_group_status_default_name:
            self.logger.info("Создание бесплатной брони")
            await self._free_booking_creation(
                booking=booking,
                booking_creation_status=booking_new_status,
                webhook_lead=webhook_lead,
                user=user
            )

        task_context: Optional[CreateTaskDTO] = await self.import_meeting_service(
            webhook_lead=webhook_lead,
            user=user,
        )

        booking: Booking | None = await self._get_booking(webhook_lead)

        if not booking:
            self.logger.warning(f"Booking {webhook_lead.lead_id} not found")
            return

        await self._meeting_workflow(booking, webhook_lead, task_context)

    async def _meeting_workflow(self, booking, webhook_lead, task_context) -> None:
        amocrm_substage: Optional[str] = AmoCRM.get_lead_substage(webhook_lead.new_status_id)
        amocrm_stage: Optional[str] = BookingStagesMapping()[amocrm_substage]
        data: dict[str, Any] = dict(
            amocrm_substage=amocrm_substage,
            amocrm_stage=amocrm_stage,
            should_be_deactivated_by_timer=False,
        )
        if self.amocrm_class.booking_payment_field_id in webhook_lead.custom_fields:
            data.update(
                price_payed=self.amocrm_class.purchase_field_mapping.get(
                    webhook_lead.custom_fields[self.amocrm_class.booking_payment_field_id].enum),
            )
        booking: Booking = await self.booking_update(booking=booking, data=data)
        await self.send_sms_to_msk_client(booking=booking)

        if self.__is_strana_lk_3011_add_enable:
            await self._update_meeting_status_add(
                booking=booking,
                amocrm_substage=amocrm_substage,
                task_context=task_context,
            )
        elif self.__is_strana_lk_3011_use_enable:
            await self._update_meeting_status_use(
                booking=booking,
                amocrm_substage=amocrm_substage,
                task_context=task_context,
            )
        elif self.__is_strana_lk_3011_off_old_enable:
            await self._update_meeting_status_ref(
                booking=booking,
                amocrm_substage=amocrm_substage,
                task_context=task_context,
            )
        else:
            await self._update_meeting_status(
                booking=booking,
                amocrm_substage=amocrm_substage,
                task_context=task_context,
            )

    async def send_sms_to_msk_client(self, booking: Booking) -> None:
        """
        Отправка смс клиенту из МСК
        """
        if booking.substages != BookingSubstages.BOOKING or not booking.user:
            # Отправляем СМС только в статусе БРОНЬ
            return
        sms_slug: str = "assign_client"
        send_sms_to_msk_client_task.delay(booking_id=booking.id, sms_slug=sms_slug)

    async def create_task_instance(
            self,
            booking_ids: list[int],
            task_context: Optional[CreateTaskDTO] = None,
    ) -> None:
        """
        Создание задачи для бронирования
        """
        await self.create_task_instance_service(booking_ids=booking_ids, task_context=task_context)

    async def update_task_instance(self, booking: Booking, task_context: CreateTaskDTO) -> None:
        """
        Обновление задачи для бронирования
        """
        status_slug: str | None = task_context.status_slug if task_context else None

        if status_slug:
            await self.update_task_instance_service(booking_id=booking.id, status_slug=status_slug)

    async def _get_user(self, webhook_lead: WebhookLead) -> User:
        """
        Получаем клиента по номеру телефона.
        Если его нет, то создаем его с теми данными, которые пришли из АМО.
        """
        user_data: dict = self._get_custom_fields(webhook_lead)
        user: User | None = await self.user_repo.retrieve(
            filters=dict(phone=user_data.get("phone"), type=UserType.CLIENT)
        )
        if not user:
            user: User = await self.user_repo.create(data=user_data)
        return user

    async def _get_booking(self, webhook_lead: WebhookLead) -> Booking | None:
        """
        Получаем сделку по amocrm_id
        """
        filters: dict[str, Any] = dict(amocrm_id=webhook_lead.lead_id)
        booking: Booking | None = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["property"],
        )
        return booking

    def _get_custom_fields(self, webhook_lead: WebhookLead) -> dict:
        """
        Парсим custom_fields и подготавливаем их к виду,
        соответствующему моделе User.
        """
        user_data = {
            "type": UserType.CLIENT
        }

        for field_id, field in webhook_lead.custom_fields.items():
            match field_id:
                case self.amocrm_class.phone_field_id:
                    if field.value is None:
                        raise AmoContactIncorrectPhoneFormatError
                    phone = parse_phone(field.value)
                    if phone is None:
                        raise AmoContactIncorrectPhoneFormatError
                    user_data["phone"] = phone
                case self.amocrm_class.email_field_id:
                    user_data["email"] = field.value
                case self.amocrm_class.birth_date_field_id:
                    user_data["birth_date"] = field.value
                case self.name_field_id:
                    user_data["name"] = field.value
                case self.surname_field_id:
                    user_data["surname"] = field.value
                case self.patronymic_field_id:
                    user_data["patronymic"] = field.value
                case self.amocrm_class.passport_field_id:
                    passport: Optional[str] = field.value
                    if passport.isdigit():
                        user_data["passport_series"] = passport[:4]
                        user_data["passport_number"] = passport[5:]
                    else:
                        *passport_series, user_data["passport_number"] = passport.split()
                        user_data["passport_series"]: Optional[str] = ''.join(passport_series) or None

        return user_data

    async def _get_booking_creation_status(self, webhook_lead) -> AmocrmStatus | None:
        """Получаем статус создания сделки"""
        booking_creation_status = await self.amocrm_status_repo.retrieve(
            filters=dict(id=webhook_lead.new_status_id),
        )
        return booking_creation_status

    async def _update_booking(self, booking, data):
        booking: Booking = await self.booking_repo.update(model=booking, data=data)
        return booking

    async def _free_booking_creation(
            self,
            booking: Booking | None,
            booking_creation_status: AmocrmStatus,
            webhook_lead: WebhookLead,
            user: User
    ) -> Booking | None:
        """Создание бесплатной брони, либо обновление существующей"""
        if not booking and booking_creation_status and webhook_lead.custom_fields.get(
                # сделка не создастся без поля expires (booking_expires_datetime_field_id из АМО)
                self.amocrm_class.booking_expires_datetime_field_id
        ):
            self.logger.info("Start booking creation (Myuutsuu)", booking_creation_status=booking_creation_status)
            booking: Booking = await self.booking_creation_service(
                webhook_lead=webhook_lead,
                amo_status=booking_creation_status,
                user_id=user.id if user else None,
            )
        elif booking and user:
            booking: Booking = await self._update_booking(booking, data=dict(user_id=user.id))
        elif not booking:
            self.logger.warning('Booking wrong webhook (Charizard)')
            return
        return booking

    async def task_created_or_updated(
            self,
            booking: Booking,
            meeting: Optional[Meeting],
            task_context: CreateTaskDTO,
    ) -> None:
        """
        Создание или обновление задачи для бронирования
        """
        task_created: bool = False
        if meeting:
            # таски для цепочки заданий Встречи
            meeting_task_exists: bool = await check_task_instance_exists(
                booking=booking,
                task_status=MeetingsSlug.START.value,
            )
            if meeting_task_exists:
                await self.update_task_instance(booking=booking, task_context=task_context)
            else:
                await self.create_task_instance(booking_ids=[booking.id], task_context=task_context)
                task_created: bool = True

        if not task_created:
            # таски для остальных цепочек заданий
            await self.create_task_instance(booking_ids=[booking.id])

    async def _update_meeting_status(
        self,
        amocrm_substage: str,
        booking: Booking,
        task_context: CreateTaskDTO,
    ) -> None:
        """
        Обновление статуса встречи сделки из амо.
        """
        filters: dict[str, Any] = dict(booking_id=booking.id)
        meeting = await self.meeting_repo.retrieve(
            filters=filters,
            related_fields=[
                "booking",
                "status",
                "calendar_event",
            ],
            prefetch_fields=["booking__agent", "booking__user"],
        )

        old_status = meeting.status if meeting and meeting.status else None
        new_status = None

        meeting_data = dict()
        if meeting and amocrm_substage == BookingSubstages.MEETING \
            and meeting.status.slug == MeetingStatusChoice.NOT_CONFIRM:
            confirm_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.CONFIRM)
            )
            new_status = confirm_meeting_status
            meeting_data.update(status_id=confirm_meeting_status.id)
            if task_context.meeting_new_date:
                task_context.update(status_slug=MeetingsSlug.CONFIRMED_RESCHEDULED.value)
            else:
                task_context.update(status_slug=MeetingsSlug.CONFIRMED.value)

        elif meeting and amocrm_substage == BookingSubstages.MEETING_IN_PROGRESS \
            and meeting.status.slug == MeetingStatusChoice.CONFIRM:
            start_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.START)
            )
            new_status = start_meeting_status
            meeting_data.update(status_id=start_meeting_status.id)
            task_context.update(status_slug=MeetingsSlug.START.value)
            if meeting.type == MeetingType.ONLINE and not meeting.meeting_link:
                await self.create_meeting_room_service(
                    unix_datetime=meeting.date.timestamp(),
                    meeting_id=meeting.id,
                )

        elif meeting and meeting.status.slug == MeetingStatusChoice.START \
            and booking.amocrm_status_id not in MEETING_STATUSES:
            finish_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.FINISH)
            )
            new_status = finish_meeting_status
            meeting_data.update(status_id=finish_meeting_status.id)
            task_context.update(status_slug=MeetingsSlug.FINISH.value)

        await self.task_created_or_updated(booking=booking, meeting=meeting, task_context=task_context)

        if meeting_data and meeting:
            update_meeting: Meeting = await self.meeting_repo.update(model=meeting, data=meeting_data)

            meeting_event_emitter.ee.emit(
                'meeting_status_changed',
                booking=booking,
                new_status=new_status,
                old_status=old_status,
            )

            prefetch_fields: list[str] = ["booking", "booking__agent", "booking__user"]
            await update_meeting.fetch_related(*prefetch_fields)
            if update_meeting.booking.agent:
                await self.send_email_to_broker(
                    meeting=update_meeting,
                    user=update_meeting.booking.agent,
                    meeting_data=meeting_data,
                )
            if update_meeting.booking.user:
                await self.send_email_to_client(
                    meeting=update_meeting,
                    user=update_meeting.booking.user,
                    meeting_data=meeting_data,
                )

    async def send_email_to_broker(
            self,
            meeting: Meeting,
            user: User,
            meeting_data: dict,
    ) -> Task | None:
        """
        Уведомляем брокера о том, что у встречи в амо изменился статус.
        @param meeting: Meeting
        @param user: User
        @param meeting_data: dict
        @return: Task
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.meeting_change_status_to_broker_mail,
            context=dict(meeting=meeting, user=user, meeting_data=meeting_data),
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
            meeting_data: dict,
    ) -> Task | None:
        """
        Уведомляем клиента о том, что у встречи в амо изменился статус.
        @param meeting: Meeting
        @param user: User
        @param meeting_data: dict
        @return: Task
        """
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.meeting_change_status_to_client_mail,
            context=dict(meeting=meeting, user=user, meeting_data=meeting_data),
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

    async def _update_meeting_status_add(
        self,
        amocrm_substage: str,
        booking: Booking,
        task_context: CreateTaskDTO,
    ) -> None:
        """
        Обновление статуса встречи сделки из амо.
        """
        filters: dict[str, Any] = dict(booking_id=booking.id)
        meeting = await self.meeting_repo.retrieve(
            filters=filters,
            related_fields=[
                "booking",
                "status",
                "status_ref",
                "calendar_event",
            ],
            prefetch_fields=["booking__agent", "booking__user"],
        )
        self.logger.info(
            f"2: _update_meeting_status_add| {meeting=} {amocrm_substage=} {booking=} {task_context=}"
        )

        # task_context = task_context if task_context else CreateTaskDTO()

        old_status = meeting.status if meeting and meeting.status else None
        new_status = None

        meeting_data = dict()
        if meeting and amocrm_substage == BookingSubstages.MEETING \
            and meeting.status.slug == MeetingStatusChoice.NOT_CONFIRM:
            confirm_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.CONFIRM)
            )
            confirm_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.CONFIRM)
            )
            new_status = confirm_meeting_status
            meeting_data.update(
                status_id=confirm_meeting_status.id,
                status_ref_id=confirm_meeting_status_ref.slug,
            )
            if task_context.meeting_new_date:
                task_context.update(status_slug=MeetingsSlug.CONFIRMED_RESCHEDULED.value)
            else:
                task_context.update(status_slug=MeetingsSlug.CONFIRMED.value)

        elif meeting and amocrm_substage == BookingSubstages.MEETING_IN_PROGRESS \
            and meeting.status.slug == MeetingStatusChoice.CONFIRM:
            start_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.START)
            )
            start_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.START)
            )
            new_status = start_meeting_status
            meeting_data.update(
                status_id=start_meeting_status.id,
                status_ref_id=start_meeting_status_ref.slug,
            )
            task_context.update(status_slug=MeetingsSlug.START.value)
            if meeting.type == MeetingType.ONLINE and not meeting.meeting_link:
                await self.create_meeting_room_service(
                    unix_datetime=meeting.date.timestamp(),
                    meeting_id=meeting.id,
                )

        elif meeting and meeting.status.slug == MeetingStatusChoice.START \
            and booking.amocrm_status_id not in MEETING_STATUSES:
            finish_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.FINISH)
            )
            finish_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.FINISH)
            )
            new_status = finish_meeting_status
            meeting_data.update(
                status_id=finish_meeting_status.id,
                status_ref_id=finish_meeting_status_ref.slug,
            )
            task_context.update(status_slug=MeetingsSlug.FINISH.value)

        await self.task_created_or_updated(booking=booking, meeting=meeting, task_context=task_context)

        if meeting_data and meeting:

            update_meeting: Meeting = await self.meeting_repo.update(model=meeting, data=meeting_data)

            meeting_event_emitter.ee.emit(
                'meeting_status_changed',
                booking=booking,
                new_status=new_status,
                old_status=old_status,
            )

            prefetch_fields: list[str] = ["booking", "booking__agent", "booking__user"]
            await update_meeting.fetch_related(*prefetch_fields)
            if update_meeting.booking.agent:
                await self.send_email_to_broker(
                    meeting=update_meeting,
                    user=update_meeting.booking.agent,
                    meeting_data=meeting_data,
                )
            if update_meeting.booking.user:
                await self.send_email_to_client(
                    meeting=update_meeting,
                    user=update_meeting.booking.user,
                    meeting_data=meeting_data,
                )

    async def _update_meeting_status_use(
        self,
        amocrm_substage: str,
        booking: Booking,
        task_context: CreateTaskDTO,
    ) -> None:
        """
        Обновление статуса встречи сделки из амо.
        """
        filters: dict[str, Any] = dict(booking_id=booking.id)
        meeting = await self.meeting_repo.retrieve(
            filters=filters,
            related_fields=[
                "booking",
                "status",
                "status_ref",
                "calendar_event",
            ],
            prefetch_fields=["booking__agent", "booking__user"],
        )
        self.logger.info(
            f"2: _update_meeting_status_use| {meeting=} {amocrm_substage=} {booking=} {task_context=}"
        )

        old_status = meeting.status if meeting and meeting.status else None
        new_status = None

        meeting_data = dict()
        if meeting and amocrm_substage == BookingSubstages.MEETING \
            and meeting.status_ref.slug == MeetingStatusChoice.NOT_CONFIRM:
            confirm_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.CONFIRM)
            )
            confirm_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.CONFIRM)
            )
            new_status = confirm_meeting_status_ref
            meeting_data.update(
                status_id=confirm_meeting_status.id,
                status_ref_id=confirm_meeting_status_ref.slug,
            )
            if task_context.meeting_new_date:
                task_context.update(status_slug=MeetingsSlug.CONFIRMED_RESCHEDULED.value)
            else:
                task_context.update(status_slug=MeetingsSlug.CONFIRMED.value)

        elif meeting and amocrm_substage == BookingSubstages.MEETING_IN_PROGRESS \
            and meeting.status_ref.slug == MeetingStatusChoice.CONFIRM:
            start_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.START)
            )
            start_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.START)
            )
            new_status = start_meeting_status_ref
            meeting_data.update(
                status_id=start_meeting_status.id,
                status_ref_id=start_meeting_status_ref.slug,
            )
            task_context.update(status_slug=MeetingsSlug.START.value)
            if meeting.type == MeetingType.ONLINE and not meeting.meeting_link:
                await self.create_meeting_room_service(
                    unix_datetime=meeting.date.timestamp(),
                    meeting_id=meeting.id,
                )

        elif meeting and meeting.status_ref.slug == MeetingStatusChoice.START \
            and booking.amocrm_status_id not in MEETING_STATUSES:
            finish_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.FINISH)
            )
            finish_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.FINISH)
            )
            new_status = finish_meeting_status_ref
            meeting_data.update(
                status_id=finish_meeting_status.id,
                status_ref_id=finish_meeting_status_ref.slug,
            )
            task_context.update(status_slug=MeetingsSlug.FINISH.value)

        await self.task_created_or_updated(booking=booking, meeting=meeting, task_context=task_context)

        if meeting_data and meeting:
            update_meeting: Meeting = await self.meeting_repo.update(model=meeting, data=meeting_data)

            meeting_event_emitter.ee.emit(
                'meeting_status_changed',
                booking=booking,
                new_status=new_status,
                old_status=old_status,
            )

            prefetch_fields: list[str] = ["booking", "booking__agent", "booking__user"]
            await update_meeting.fetch_related(*prefetch_fields)
            if update_meeting.booking.agent:
                await self.send_email_to_broker(
                    meeting=update_meeting,
                    user=update_meeting.booking.agent,
                    meeting_data=meeting_data,
                )
            if update_meeting.booking.user:
                await self.send_email_to_client(
                    meeting=update_meeting,
                    user=update_meeting.booking.user,
                    meeting_data=meeting_data,
                )

    async def _update_meeting_status_ref(
        self,
        amocrm_substage: str,
        booking: Booking,
        task_context: CreateTaskDTO,
    ) -> None:
        """
        Обновление статуса встречи сделки из амо.
        """
        filters: dict[str, Any] = dict(booking_id=booking.id)
        meeting = await self.meeting_repo.retrieve(
            filters=filters,
            related_fields=[
                "booking",
                "status_ref",
                "calendar_event",
            ],
            prefetch_fields=["booking__agent", "booking__user"],
        )
        self.logger.info(
            f"2: _update_meeting_status_ref| {meeting=} {amocrm_substage=} {booking=} {task_context=}"
        )

        old_status = meeting.status if meeting and meeting.status else None
        new_status = None

        meeting_data = dict()
        if meeting and amocrm_substage == BookingSubstages.MEETING \
            and meeting.status_ref.slug == MeetingStatusChoice.NOT_CONFIRM:
            confirm_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.CONFIRM)
            )
            new_status = confirm_meeting_status_ref
            meeting_data.update(status_ref_id=confirm_meeting_status_ref.slug)
            if task_context.meeting_new_date:
                task_context.update(status_slug=MeetingsSlug.CONFIRMED_RESCHEDULED.value)
            else:
                task_context.update(status_slug=MeetingsSlug.CONFIRMED.value)

        elif meeting and amocrm_substage == BookingSubstages.MEETING_IN_PROGRESS \
            and meeting.status_ref.slug == MeetingStatusChoice.CONFIRM:
            start_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.START)
            )
            new_status = start_meeting_status_ref
            meeting_data.update(status_ref_id=start_meeting_status_ref.slug)
            task_context.update(status_slug=MeetingsSlug.START.value)
            if meeting.type == MeetingType.ONLINE and not meeting.meeting_link:
                await self.create_meeting_room_service(
                    unix_datetime=meeting.date.timestamp(),
                    meeting_id=meeting.id,
                )

        elif meeting and meeting.status_ref.slug == MeetingStatusChoice.START \
            and booking.amocrm_status_id not in MEETING_STATUSES:
            finish_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.FINISH)
            )
            new_status = finish_meeting_status_ref
            meeting_data.update(status_ref_id=finish_meeting_status_ref.slug)
            task_context.update(status_slug=MeetingsSlug.FINISH.value)

        await self.task_created_or_updated(booking=booking, meeting=meeting, task_context=task_context)

        if meeting_data and meeting:

            meeting_event_emitter.ee.emit(
                'meeting_status_changed',
                booking=booking,
                new_status=new_status,
                old_status=old_status,
            )

            update_meeting: Meeting = await self.meeting_repo.update(model=meeting, data=meeting_data)
            prefetch_fields: list[str] = ["booking", "booking__agent", "booking__user"]
            await update_meeting.fetch_related(*prefetch_fields)
            if update_meeting.booking.agent:
                await self.send_email_to_broker(
                    meeting=update_meeting,
                    user=update_meeting.booking.agent,
                    meeting_data=meeting_data,
                )
            if update_meeting.booking.user:
                await self.send_email_to_client(
                    meeting=update_meeting,
                    user=update_meeting.booking.user,
                    meeting_data=meeting_data,
                )

    @staticmethod
    def _parse_data(
            data: dict[str, Any]
    ) -> WebhookLead:
        lead_id: Optional[int] = None
        pipeline_id: Optional[int] = None
        new_status_id: Optional[int] = None
        tags: dict[str, Any] = {}
        custom_fields: dict[str, Any] = {}
        for key, value in data.items():
            if "custom_fields" in key:
                key_components: list[str] = key.split("[")
                if len(key_components) >= 5:
                    field_number: str = key_components[4][:-1]
                    if field_number not in custom_fields:
                        custom_fields[field_number]: dict[str, Any] = {}
                    # проверяем, что пришло поле id и никакое другое (не account_id, type_id и т.д)
                    # иначе id-перезаписываются, т.к у всех полей есть account_id - одинаковый,
                    if key.split("[")[-1] == "id]":
                        custom_fields[field_number]["id"]: Union[str, int] = int(value[0])
                    if "name" in key:
                        custom_fields[field_number]["name"]: Union[str, int] = value[0]
                    if "values" in key:
                        _, value_enum = key.split("values")
                        if "value" in value_enum:
                            custom_fields[field_number]["value"]: Union[str, int] = value[0]
                        if "enum" in value_enum:
                            custom_fields[field_number]["enum"]: Union[str, int] = int(value[0])
            elif "tags" in key:
                key_components: list[str] = key.split("[")
                if len(key_components) >= 5:
                    field_number: str = key_components[4][:-1]
                    if field_number not in tags:
                        tags[field_number]: dict[str, Any] = {}
                    if "id" in key:
                        tags[field_number]["id"] = int(value[0])
                    if "name" in key:
                        tags[field_number]["name"] = value[0]

            elif key in {
                # Возможно будут и другие поля, если будут, надо добавить их сюда.
                # Аналогично и для pipeline_id, new_status_id
                "leads[sensei][0][id]",
            }:
                lead_id = int(value[0])
            elif key in {
                "leads[sensei][0][status_id]",
            }:
                new_status_id = int(value[0])
            elif key in {
                "leads[sensei][0][pipeline_id]",
            }:
                pipeline_id = int(value[0])
        custom_fields_dict: dict[int, CustomFieldValue] = {
            field["id"]: CustomFieldValue(
                name=field.get("name"),
                value=field.get("value"),
                enum=field.get("enum"),
            )
            for field in custom_fields.values()
        }
        tags_dict: dict[int, str] = {tag.get("id"): tag.get("name") for tag in tags.values()}

        lead = WebhookLead(
            lead_id=lead_id,
            pipeline_id=pipeline_id,
            new_status_id=new_status_id,
            custom_fields=custom_fields_dict,
            tags=tags_dict,
        )
        return lead

    @property
    def __is_strana_lk_3011_add_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_add)

    @property
    def __is_strana_lk_3011_use_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_use)

    @property
    def __is_strana_lk_3011_off_old_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_off_old)
