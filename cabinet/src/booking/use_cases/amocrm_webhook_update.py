"""
AMOCRM webhook_status
"""
import json
from asyncio import Task
from datetime import datetime, timedelta
from secrets import compare_digest
from typing import Any, Optional, Type, Union
from urllib.parse import parse_qs, unquote

import structlog
from fastapi import BackgroundTasks

from common.amocrm import AmoCRM
from common.amocrm.repos import AmoStatusesRepo
from common.backend.models.amocrm import AmocrmStatus
from common.email import EmailService
from common.sentry.utils import send_sentry_log
from common.unleash.client import UnleashClient
from config.feature_flags import FeatureFlags
from src.amocrm.repos import AmocrmStatusRepo
from src.events.repos import CalendarEventRepo
from src.meetings.constants import MeetingStatusChoice
from src.meetings.constants import MeetingType
from src.meetings.repos import MeetingRepo, Meeting, MeetingStatusRepo
from src.meetings.repos import MeetingStatusRefRepo
from src.meetings.services import CreateRoomService, ImportMeetingFromAmoService
from src.notifications.services import GetEmailTemplateService
from src.payments.repos import PurchaseAmoMatrix, PurchaseAmoMatrixRepo
from src.projects.constants import ProjectStatus
from src.projects.repos import ProjectRepo, Project
from src.properties.repos import Property
from src.task_management.constants import FixationExtensionSlug, BOOKING_UPDATE_FIXATION_STATUSES
from src.task_management.constants import MeetingsSlug, UpdateMeetingGroupStatusSlug
from src.task_management.dto import CreateTaskDTO
from src.task_management.services import CreateTaskInstanceService, UpdateTaskInstanceStatusService
from src.task_management.utils import check_task_instance_exists
from src.users.repos import UserRepo, User
from src.users.services import (
    ImportAgentFromAmoService,
    ImportClientFromAmoService,
    CheckPinningStatusServiceV2,
)
from ..constants import BookingSubstages
from ..entities import BaseBookingCase
from ..loggers.wrappers import booking_changes_logger
from ..mixins import BookingLogMixin
from ..repos import Booking, BookingRepo, WebhookRequestRepo
from ..services import BookingCreationFromAmoService
from ..tasks import activate_bookings_task, deactivate_bookings_task, send_sms_to_msk_client_task
from ..types import (
    BookingAmoCRM, BookingPropertyRepo, BookingRequest, CustomFieldValue, WebhookLead
)
from src.meetings.event_emitter_handlers import meeting_event_emitter

ASSIGN_AGENT_STATUSES = [
    AmoCRM.TMNStatuses.ASSIGN_AGENT,
    AmoCRM.MSKStatuses.ASSIGN_AGENT,
    AmoCRM.SPBStatuses.ASSIGN_AGENT,
    AmoCRM.EKBStatuses.ASSIGN_AGENT,
    AmoCRM.TestStatuses.ASSIGN_AGENT,
]

START_STATUSES = [
    AmoCRM.TMNStatuses.START,
    AmoCRM.MSKStatuses.START,
    AmoCRM.SPBStatuses.START,
    AmoCRM.EKBStatuses.START,
    AmoCRM.TestStatuses.START,
]


class AmoCRMWebhookUpdateCase(BaseBookingCase, BookingLogMixin):
    """
    Update Вебхук АМО
    """
    query_type: str = "changePropertyStatus"
    query_name: str = "changePropertyStatus.graphql"
    query_directory: str = "/src/booking/queries/"
    amocrm_group_status_default_name: str = "Бронь"
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
        logger: Optional[Any] = structlog.getLogger(__name__),
        create_booking_log_task: Optional[Any] = None,
        create_task_instance_service: CreateTaskInstanceService,
        update_task_instance_service: UpdateTaskInstanceStatusService,
        check_pinning: CheckPinningStatusServiceV2,
        email_class: Type[EmailService],
        get_email_template_service: GetEmailTemplateService,
        import_contact_service: ImportClientFromAmoService,
        import_agent_service: ImportAgentFromAmoService,
        import_meeting_service: ImportMeetingFromAmoService,
        booking_creation_service: BookingCreationFromAmoService,
        purchase_amo_matrix_repo: Type[PurchaseAmoMatrixRepo],
        # change_mortgage_ticket_status_service: ChangeMortgageTicketStatusService,
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
        self.check_pinning: CheckPinningStatusServiceV2 = check_pinning
        self.email_class: Type[EmailService] = email_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.import_contact_service: ImportClientFromAmoService = import_contact_service
        self.import_agent_service: ImportAgentFromAmoService = import_agent_service
        self.import_meeting_service: ImportMeetingFromAmoService = import_meeting_service
        self.booking_creation_service: BookingCreationFromAmoService = booking_creation_service
        self.purchase_amo_matrix_repo: PurchaseAmoMatrixRepo = purchase_amo_matrix_repo()
        # self.change_mortgage_ticket_status_service = change_mortgage_ticket_status_service

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

    def _is_secret_valid(self, secret) -> bool:
        if compare_digest(secret, self.secret):
            return True
        self.logger.error("Booking resource not found")
        return False

    async def _send_log_no_custom_fields(self, webhook_lead, payload) -> None:
        if not webhook_lead.custom_fields:
            sentry_ctx: dict[str, Any] = dict(
                webhook_lead=webhook_lead,
                custom_fields=webhook_lead.custom_fields,
                payload=payload,
            )
            await send_sentry_log(
                tag="webhook update",
                message="miss custom_fields",
                context=sentry_ctx,
            )
            self.logger.error("Booking update webhook fatal error")

    async def _have_booking_and_user(self, booking: Booking, user_id: int) -> Booking:
        updated_booking: Booking = await self.booking_repo.update(model=booking, data=dict(user_id=user_id))
        return updated_booking

    async def _get_booking(self, webhook_lead_lead_id: int) -> Booking:
        filters: dict[str, Any] = dict(amocrm_id=webhook_lead_lead_id)
        booking: Optional[Booking] = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["property"],
        )

        return booking

    def _is_valid_pipeline(self, webhook_lead_pipeline_id) -> bool:
        """
        Не обновляем сделки из воронок, кроме городов
        """
        if webhook_lead_pipeline_id in self.amocrm_class.sales_pipeline_ids:
            return True
        return False

    async def __call__(self, secret: str, payload: bytes, *args, **kwargs) -> None:
        data: dict[str, Any] = parse_qs(unquote(payload.decode("utf-8")))

        if not self._is_secret_valid(secret):
            return

        webhook_lead: WebhookLead = self._parse_data(data=data)
        self.logger.info(f"{webhook_lead.lead_id=}")

        user: User = await self.import_contact_service(webhook_lead=webhook_lead)

        if self.__is_strana_lk_3519_enable:
            # if (datetime.utcnow() - datetime.fromtimestamp(webhook_lead.updated_at)) > timedelta(seconds=20):
            await self.import_agent_service(webhook_lead=webhook_lead)

        task_context: Optional[CreateTaskDTO] = await self.import_meeting_service(webhook_lead=webhook_lead, user=user)
        if not webhook_lead.custom_fields:
            await self._send_log_no_custom_fields(webhook_lead, payload)
            return

        amocrm_substage: Optional[str] = AmoCRM.get_lead_substage(webhook_lead.new_status_id)
        booking: Booking = await self._get_booking(webhook_lead.lead_id)

        if booking and user:
            booking: Booking = await self._have_booking_and_user(booking, user.id)
        elif not booking:
            self.logger.warning('Booking wrong status webhook')
            return

        await self._update_booking_custom_fields(booking, webhook_lead)
        # await self._update_mortgage_ticket_status(booking=booking)

        if booking.user and UnleashClient().is_enabled(FeatureFlags.check_pinning_webhook):
            await self._check_user_pinning_status(booking, webhook_lead, amocrm_substage)

        if not self._is_valid_pipeline(webhook_lead.pipeline_id):
            if booking.active:
                await self.booking_deactivate(booking=booking, data=data)
            return

        await self._update_price_workflow(booking, webhook_lead)
        await self._meeting_workflow(booking, webhook_lead, task_context)

    async def _update_price_workflow(self, booking, webhook_lead) -> None:
        has_property: bool = False
        amocrm_substage: Optional[str] = AmoCRM.get_lead_substage(webhook_lead.new_status_id)
        property_final_price: Optional[int] = webhook_lead.custom_fields.get(
            self.amocrm_class.property_final_price_field_id, CustomFieldValue()
        ).value
        price_with_sale: Optional[int] = webhook_lead.custom_fields.get(
            self.amocrm_class.property_price_with_sale_field_id, CustomFieldValue()
        ).value

        stages_valid = self._is_stage_valid(amocrm_substage=amocrm_substage)
        if webhook_lead.custom_fields.get(self.amocrm_class.property_field_id, CustomFieldValue()).value:
            has_property = True
        # Если сделка находится в определённом статусе, который не требует проверки наличия квартиры
        # (Фиксация клиента за АН), то пропускаем этот шаг
        booking_in_safe_status = booking.amocrm_substage in [BookingSubstages.ASSIGN_AGENT]
        if ((not has_property and not booking_in_safe_status) or not stages_valid) and booking.active:
            booking_data: dict = dict(
                booking=booking,
                webhook_lead=webhook_lead,
                stages_valid=stages_valid
            )
            self.background_tasks.add_task(deactivate_bookings_task, booking_data)

        elif has_property and stages_valid and not booking.active:
            booking_data: dict = dict(
                booking=booking,
                webhook_lead=webhook_lead,
                property_final_price=property_final_price,
                price_with_sale=price_with_sale,
                amocrm_substage=amocrm_substage,
            )
            self.background_tasks.add_task(activate_bookings_task, booking_data)

        booking_final_payment_amount = property_final_price or price_with_sale
        if booking_final_payment_amount and booking_final_payment_amount != 0:
            data = dict(final_payment_amount=booking_final_payment_amount)
            booking: Booking = await self.booking_update(booking=booking, data=data)
            _property: Property = await self.property_repo.retrieve(filters=dict(id=booking.property_id))
            if _property:
                data = dict(final_price=price_with_sale or property_final_price)
                await self.property_repo.update(model=_property, data=data)

    async def _meeting_workflow(self, booking, webhook_lead, task_context) -> None:
        sentry_ctx: dict[str, Any] = dict(
            booking=booking,
            task_context=task_context,
        )
        await send_sentry_log(
            tag="webhook update",
            message="_meeting_workflow create meeting",
            context=sentry_ctx,
        )
        await self.create_task_instance(booking_ids=[booking.id], task_context=task_context)

    async def _update_meeting_status(
        self,
        new_status_id: int,
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

        task_context = task_context if task_context else CreateTaskDTO()

        webhook_lead_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
            filters=dict(id=new_status_id),
            related_fields=["group_status"],
        )
        if not webhook_lead_status or not webhook_lead_status.group_status:
            self.logger.info(f"Не найден амо статус или групповой статус для {new_status_id=}")
            amocrm_group_status_name = ""
        else:
            amocrm_group_status_name = webhook_lead_status.group_status.name
            self.logger.info(f"Найден групповой статус {amocrm_group_status_name=}")

        old_status = meeting.status if meeting and meeting.status else None
        new_status = None

        meeting_data = dict()
        if meeting and (
            amocrm_group_status_name == UpdateMeetingGroupStatusSlug.MEETING
            or amocrm_substage == BookingSubstages.MEETING
        ) and meeting.status.slug == MeetingStatusChoice.NOT_CONFIRM:
            confirm_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.CONFIRM)
            )
            new_status = confirm_meeting_status
            meeting_data.update(status_id=confirm_meeting_status.id)
            if task_context.meeting_new_date:
                task_context.update(status_slug=MeetingsSlug.CONFIRMED_RESCHEDULED.value)
            else:
                task_context.update(status_slug=MeetingsSlug.CONFIRMED.value)

        elif meeting and (
            amocrm_group_status_name == UpdateMeetingGroupStatusSlug.MEETING_IN_PROGRESS
            or amocrm_substage == BookingSubstages.MEETING_IN_PROGRESS
        ) and meeting.status.slug == MeetingStatusChoice.CONFIRM:
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
        elif meeting and meeting.status.slug == MeetingStatusChoice.START and (
            (
                amocrm_group_status_name
                and amocrm_group_status_name not in [
                    UpdateMeetingGroupStatusSlug.MAKE_APPOINTMENT,
                    UpdateMeetingGroupStatusSlug.MEETING,
                    UpdateMeetingGroupStatusSlug.MEETING_IN_PROGRESS,
                ]
            ) or amocrm_substage not in [
                BookingSubstages.MAKE_APPOINTMENT,
                BookingSubstages.MEETING,
                BookingSubstages.MEETING_IN_PROGRESS,
            ]
        ):
            finish_meeting_status = await self.meeting_status_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.FINISH)
            )
            new_status = finish_meeting_status
            meeting_data.update(status_id=finish_meeting_status.id)
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

    async def _update_meeting_status_add(
        self,
        new_status_id: int,
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
            f"2: _update_meeting_status_add| {meeting=} {new_status_id=} {amocrm_substage=} {booking=} {task_context=}"
        )
        task_context = task_context if task_context else CreateTaskDTO()

        webhook_lead_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
            filters=dict(id=new_status_id),
            related_fields=["group_status"],
        )
        if not webhook_lead_status or not webhook_lead_status.group_status:
            self.logger.info(f"Не найден амо статус или групповой статус для {new_status_id=}")
            amocrm_group_status_name = ""
        else:
            amocrm_group_status_name = webhook_lead_status.group_status.name
            self.logger.info(f"Найден групповой статус {amocrm_group_status_name=}")

        old_status = meeting.status if meeting and meeting.status else None
        new_status = None

        meeting_data = dict()
        if meeting and (
            amocrm_group_status_name == UpdateMeetingGroupStatusSlug.MEETING
            or amocrm_substage == BookingSubstages.MEETING
        ) and meeting.status.slug == MeetingStatusChoice.NOT_CONFIRM:
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

        elif meeting and (
            amocrm_group_status_name == UpdateMeetingGroupStatusSlug.MEETING_IN_PROGRESS
            or amocrm_substage == BookingSubstages.MEETING_IN_PROGRESS
        ) and meeting.status.slug == MeetingStatusChoice.CONFIRM:
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

        elif meeting and meeting.status.slug == MeetingStatusChoice.START and (
            (
                amocrm_group_status_name
                and amocrm_group_status_name not in [
                    UpdateMeetingGroupStatusSlug.MAKE_APPOINTMENT,
                    UpdateMeetingGroupStatusSlug.MEETING,
                    UpdateMeetingGroupStatusSlug.MEETING_IN_PROGRESS,
                ]
            ) or amocrm_substage not in [
                BookingSubstages.MAKE_APPOINTMENT,
                BookingSubstages.MEETING,
                BookingSubstages.MEETING_IN_PROGRESS,
            ]
        ):
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

    async def _update_meeting_status_use(
        self,
        new_status_id: int,
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
            f"2: _update_meeting_status_use| {meeting=} {new_status_id=} {amocrm_substage=} {booking=} {task_context=}"
        )

        task_context = task_context if task_context else CreateTaskDTO()

        webhook_lead_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
            filters=dict(id=new_status_id),
            related_fields=["group_status"],
        )
        if not webhook_lead_status or not webhook_lead_status.group_status:
            self.logger.info(f"Не найден амо статус или групповой статус для {new_status_id=}")
            amocrm_group_status_name = ""
        else:
            amocrm_group_status_name = webhook_lead_status.group_status.name
            self.logger.info(f"Найден групповой статус {amocrm_group_status_name=}")

        old_status = meeting.status if meeting and meeting.status else None
        new_status = None

        meeting_data = dict()
        if meeting and (
            amocrm_group_status_name == UpdateMeetingGroupStatusSlug.MEETING
            or amocrm_substage == BookingSubstages.MEETING
        ) and meeting.status.slug == MeetingStatusChoice.NOT_CONFIRM:
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

        elif meeting and (
            amocrm_group_status_name == UpdateMeetingGroupStatusSlug.MEETING_IN_PROGRESS
            or amocrm_substage == BookingSubstages.MEETING_IN_PROGRESS
        ) and meeting.status.slug == MeetingStatusChoice.CONFIRM:
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

        elif meeting and meeting.status.slug == MeetingStatusChoice.START and (
            (
                amocrm_group_status_name
                and amocrm_group_status_name not in [
                    UpdateMeetingGroupStatusSlug.MAKE_APPOINTMENT,
                    UpdateMeetingGroupStatusSlug.MEETING,
                    UpdateMeetingGroupStatusSlug.MEETING_IN_PROGRESS,
                ]
            ) or amocrm_substage not in [
                BookingSubstages.MAKE_APPOINTMENT,
                BookingSubstages.MEETING,
                BookingSubstages.MEETING_IN_PROGRESS,
            ]
        ):
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

    async def _update_meeting_status_ref(
        self,
        new_status_id: int,
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
            f"2: _update_meeting_status_ref| {meeting=} {new_status_id=} {amocrm_substage=} {booking=} {task_context=}"
        )

        task_context = task_context if task_context else CreateTaskDTO()

        webhook_lead_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
            filters=dict(id=new_status_id),
            related_fields=["group_status"],
        )
        if not webhook_lead_status or not webhook_lead_status.group_status:
            self.logger.info(f"Не найден амо статус или групповой статус для {new_status_id=}")
            amocrm_group_status_name = ""
        else:
            amocrm_group_status_name = webhook_lead_status.group_status.name
            self.logger.info(f"Найден групповой статус {amocrm_group_status_name=}")

        old_status = meeting.status if meeting and meeting.status else None
        new_status = None

        meeting_data = dict()
        if meeting and (
            amocrm_group_status_name == UpdateMeetingGroupStatusSlug.MEETING
            or amocrm_substage == BookingSubstages.MEETING
        ) and meeting.status.slug == MeetingStatusChoice.NOT_CONFIRM:
            confirm_meeting_status_ref = await self.meeting_status_ref_repo.retrieve(
                filters=dict(slug=MeetingStatusChoice.CONFIRM)
            )
            new_status = confirm_meeting_status_ref
            meeting_data.update(status_ref_id=confirm_meeting_status_ref.slug)
            if task_context.meeting_new_date:
                task_context.update(status_slug=MeetingsSlug.CONFIRMED_RESCHEDULED.value)
            else:
                task_context.update(status_slug=MeetingsSlug.CONFIRMED.value)

        elif meeting and (
            amocrm_group_status_name == UpdateMeetingGroupStatusSlug.MEETING_IN_PROGRESS
            or amocrm_substage == BookingSubstages.MEETING_IN_PROGRESS
        ) and meeting.status.slug == MeetingStatusChoice.CONFIRM:
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

        elif meeting and meeting.status.slug == MeetingStatusChoice.START and (
            (
                amocrm_group_status_name
                and amocrm_group_status_name not in [
                    UpdateMeetingGroupStatusSlug.MAKE_APPOINTMENT,
                    UpdateMeetingGroupStatusSlug.MEETING,
                    UpdateMeetingGroupStatusSlug.MEETING_IN_PROGRESS,
                ]
            ) or amocrm_substage not in [
                BookingSubstages.MAKE_APPOINTMENT,
                BookingSubstages.MEETING,
                BookingSubstages.MEETING_IN_PROGRESS,
            ]
        ):
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
    def _is_stage_valid(amocrm_substage: str) -> bool:
        """Считаем ли мы сделку из AmoCRM валидной.

        Валидной считается сделка, у которой есть привязка к квартире.
        Такие сделки имеют, как минимум, статус "Бронь".

        У валидных сделок забронированы/проданы квартиры в profitbase.
        """
        # Если стадия бронирования из AmoCRM не участвует в логике ЛК, сделка невалидна
        # (например, "Принимают решение", "Назначить встречу" или "Первичный контакт")
        if amocrm_substage is None:
            return False

        # Сделка невалидна, если в AmoCRM статус "Закрыто и не реализовано" или "Расторжение"
        if amocrm_substage in [BookingSubstages.TERMINATION, BookingSubstages.UNREALIZED]:
            return False

        return True

    @staticmethod
    def _parse_data(
            data: dict[str, Any]
    ) -> WebhookLead:
        """
        parse webhook data
        """
        lead_id: Optional[int] = None
        pipeline_id: Optional[int] = None
        new_status_id: Optional[int] = None
        tags: dict[str, Any] = {}
        custom_fields: dict[str, Any] = {}
        updated_at: Optional[int] = None
        for key, value in data.items():
            if "custom_fields" in key:
                key_components: list[str] = key.split("[")
                if len(key_components) >= 5:
                    field_number: str = key_components[4][:-1]
                    if field_number not in custom_fields:
                        custom_fields[field_number]: dict[str, Any] = {}
                    if "id" in key:
                        custom_fields[field_number]["id"]: Union[str, int] = int(value[0])
                    if "name" in key:
                        custom_fields[field_number]["name"]: Union[str, int] = value[0]
                    if "values" in key and "value" in key:
                        custom_fields[field_number]["value"]: Union[str, int] = value[0]
                    if "values" in key and "enum" in key:
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
                "leads[status][0][id]",
                "leads[update][0][id]",
                "leads[create][0][id]",
                "leads[add][0][id]",
            }:
                lead_id = int(value[0])
            elif key in {
                "leads[status][0][status_id]",
                "leads[update][0][status_id]",
                "leads[create][0][status_id]",
                "leads[add][0][status_id]",
            }:
                new_status_id = int(value[0])
            elif key in {
                "leads[status][0][pipeline_id]",
                "leads[update][0][pipeline_id]",
                "leads[create][0][pipeline_id]",
                "leads[add][0][pipeline_id]",
            }:
                pipeline_id = int(value[0])
            elif key in {
                "leads[status][0][updated_at]",
                "leads[update][0][updated_at]",
                "leads[create][0][updated_at]",
                "leads[add][0][updated_at]",
            }:
                updated_at = int(value[0])
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
            updated_at=updated_at,
        )
        return lead

    async def _update_booking_custom_fields(self, booking: Booking, webhook_lead: WebhookLead) -> None:
        """
        update booking custom fields
        """
        custom_fields_dict = webhook_lead.custom_fields
        tags = json.dumps(list(webhook_lead.tags.values()))
        commission: Optional[int] = custom_fields_dict.get(self.amocrm_class.commission, CustomFieldValue()).value
        commission_value: Optional[int] = custom_fields_dict.get(self.amocrm_class.commission_value,
                                                                 CustomFieldValue()).value
        final_discount = webhook_lead.custom_fields.get(
            self.amocrm_class.booking_final_discount_field_id)
        final_additional_options = webhook_lead.custom_fields.get(
            self.amocrm_class.booking_final_additional_options_field_id)
        project_enum: int = webhook_lead.custom_fields.get(self.amocrm_class.project_field_id, CustomFieldValue()).enum
        project: Optional[Project] = await self.project_repo.retrieve(filters=dict(amocrm_enum=project_enum,
                                                                                   status=ProjectStatus.CURRENT))

        booking_purchase_data: Optional[dict] = None
        if purchase_type_enum := webhook_lead.custom_fields.get(
            self.amocrm_class.booking_payment_type_field_id, CustomFieldValue()
        ).enum:
            purchase_amo: Optional[PurchaseAmoMatrix] = await self.purchase_amo_matrix_repo.retrieve(
                filters=dict(amo_payment_type=purchase_type_enum),
                related_fields=["mortgage_type", "payment_method"],
            )
            if not purchase_amo:
                purchase_amo: PurchaseAmoMatrix = await self.purchase_amo_matrix_repo.retrieve(
                    filters=dict(default=True),
                    related_fields=["mortgage_type", "payment_method"],
                )
            booking_purchase_data = dict(
                amo_payment_method=purchase_amo.payment_method,
                mortgage_type=purchase_amo.mortgage_type,
            ) if purchase_amo else None

        data: dict = dict(
            commission=commission,
            commission_value=commission_value,
            tags=tags,
            final_discount=final_discount.value if final_discount else None,
            final_additional_options=final_additional_options.value if final_additional_options else None,
            project=project,
        )
        if booking_purchase_data:
            data.update(booking_purchase_data)

        await self.booking_repo.update(model=booking, data=data)

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

    async def _check_task_instance_exists(self, booking: Booking) -> bool:
        """
        Проверка наличия задачи для бронирования
        """
        await booking.fetch_related('task_instances')
        if booking.task_instances:
            return True
        return False

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

    async def _check_user_pinning_status(
            self,
            booking: Booking,
            webhook_lead: WebhookLead,
            amocrm_substage: Optional[str],
    ) -> None:
        """
        check user pinning status
        """
        await booking.fetch_related('user', 'amocrm_status', 'amocrm_status__pipeline')

        if amocrm_substage != booking.amocrm_substage:
            await self.check_pinning(user_id=booking.user.id)
            return

        if booking.amocrm_status:
            if booking.amocrm_status.pipeline.id != webhook_lead.pipeline_id:
                await self.check_pinning(user_id=booking.user.id)

    async def send_sms_to_msk_client(self, booking: Booking) -> None:
        """
        Отправка смс клиенту из МСК
        """
        if booking.substages != BookingSubstages.BOOKING or not booking.user:
            # Отправляем СМС только в статусе БРОНЬ
            return
        sms_slug: str = "assign_client"
        send_sms_to_msk_client_task.delay(booking_id=booking.id, sms_slug=sms_slug)

    async def send_email_to_broker(
            self,
            meeting: Meeting,
            user: User,
            meeting_data: dict,
    ) -> Task:
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
    ) -> Task:
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

    # async def _update_mortgage_ticket_status(self, booking: Booking) -> None:
    #     """
    #     Обновление статуса заявки на ипотеку
    #     """
    #     self.change_mortgage_ticket_status_service.as_task(booking_id=booking.id)

    @property
    def __is_strana_lk_3011_add_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_add)

    @property
    def __is_strana_lk_3011_use_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_use)

    @property
    def __is_strana_lk_3011_off_old_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3011_off_old)

    @property
    def __is_strana_lk_3519_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3519)
