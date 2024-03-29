"""
AMOCRM webhook_status
"""
import json
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
from src.meetings.repos import MeetingRepo, MeetingStatusRepo
from src.meetings.repos import MeetingStatusRefRepo
from src.meetings.services import CreateRoomService, ImportMeetingFromAmoService
from src.notifications.services import GetEmailTemplateService
from src.projects.constants import ProjectStatus
from src.projects.repos import ProjectRepo, Project
from src.properties.repos import Property
from src.task_management.constants import FixationExtensionSlug, BOOKING_UPDATE_FIXATION_STATUSES
from src.task_management.dto import CreateTaskDTO
from src.task_management.services import CreateTaskInstanceService, UpdateTaskInstanceStatusService
from src.users.repos import UserRepo, User
from src.users.services import CheckPinningStatusServiceV2
from src.users.services import ImportClientFromAmoService
from ..constants import BookingSubstages, CancelRewardComment, CancelRewardBookingGroupStatus
from ..entities import BaseBookingCase
from ..loggers.wrappers import booking_changes_logger
from ..mixins import BookingLogMixin
from ..repos import Booking, BookingRepo, WebhookRequestRepo
from ..services import BookingCreationFromAmoService
from ..tasks import activate_bookings_task, deactivate_bookings_task
from ..types import (
    BookingAmoCRM, BookingPropertyRepo, BookingRequest, CustomFieldValue, WebhookLead
)
from ..event_emitter_handlers import event_emitter

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


class AmoCRMWebhookStatusCase(BaseBookingCase, BookingLogMixin):
    """
    Status Вебхук АМО
    """
    query_type: str = "changePropertyStatus"
    query_name: str = "changePropertyStatus.graphql"
    query_directory: str = "/src/booking/queries/"
    amocrm_group_status_default_name: str = "Бронь"

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
        import_meeting_service: ImportMeetingFromAmoService,
        booking_creation_service: BookingCreationFromAmoService,
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

    def _is_secret_valid(self, secret) -> bool:
        """Проверка корректности секрета"""
        if compare_digest(secret, self.secret):
            return True
        self.logger.error("Booking resource not found")
        return False

    async def _send_log_no_custom_fields(self, webhook_lead, payload) -> None:
        """Отправка логов, если не пришли custom_fields"""
        if not webhook_lead.custom_fields:
            sentry_ctx: dict[str, Any] = dict(
                webhook_lead=webhook_lead,
                custom_fields=webhook_lead.custom_fields,
                payload=payload,
            )
            await send_sentry_log(
                tag="webhook status",
                message="miss custom_fields",
                context=sentry_ctx,
            )
            self.logger.error("Booking status webhook fatal error")

    async def _have_booking_and_user(self, booking: Booking, user_id: int) -> Booking:
        updated_booking: Booking = await self.booking_repo.update(model=booking, data=dict(user_id=user_id))
        return updated_booking

    async def _get_booking(self, webhook_lead_lead_id: int) -> Booking:
        filters: dict[str, Any] = dict(amocrm_id=webhook_lead_lead_id)
        booking: Optional[Booking] = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["property"],
            prefetch_fields=["amocrm_status__group_status"],
        )

        return booking

    @staticmethod
    async def _check_status_for_reward_cancel(booking: Booking) -> None:
        if (
            booking and booking.amocrm_status and booking.amocrm_status.group_status
            and booking.loyalty_discount and booking.loyalty_discount_name
        ):
            if booking.amocrm_status.group_status.name in [
                CancelRewardBookingGroupStatus.START,
                CancelRewardBookingGroupStatus.MAKE_DECISION,
            ]:
                event_emitter.ee.emit('cancel_loyalty_reward_from_booking', booking, CancelRewardComment.UNBOOKED)
            elif booking.amocrm_status.group_status.name == CancelRewardBookingGroupStatus.UNREALIZED:
                event_emitter.ee.emit('cancel_loyalty_reward_from_booking', booking, CancelRewardComment.CANCELED)

    async def _get_booking_creation_status(self, webhook_lead_pipeline_id):
        booking_creation_status = await self.amocrm_status_repo.retrieve(
            filters=dict(
                pipeline_id=webhook_lead_pipeline_id,
                group_status__name__icontains=self.amocrm_group_status_default_name,
            )
        )
        return booking_creation_status

    def _need_create_booking(self, booking: Booking, booking_creation_status, webhook_lead_custom_fields) -> bool:
        """
        Проверяем: Сможем ли создать сделку?
        Сделка не создастся без поля expires (booking_expires_datetime_field_id из АМО)
        """
        if (
                not booking
                and booking_creation_status
                and webhook_lead_custom_fields.get(self.amocrm_class.booking_expires_datetime_field_id)
        ):
            return True

        return False

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
        print(webhook_lead.lead_id)

        user: User = await self.import_contact_service(webhook_lead=webhook_lead)
        task_context: Optional[CreateTaskDTO] = await self.import_meeting_service(webhook_lead=webhook_lead, user=user)
        if not webhook_lead.custom_fields:
            await self._send_log_no_custom_fields(webhook_lead, payload)
            return

        amocrm_substage: Optional[str] = AmoCRM.get_lead_substage(webhook_lead.new_status_id)
        booking: Booking = await self._get_booking(webhook_lead.lead_id)
        await self._check_status_for_reward_cancel(booking)

        booking_creation_status = await self._get_booking_creation_status(webhook_lead.pipeline_id)

        if booking and user:
            booking: Booking = await self._have_booking_and_user(booking, user.id)

        elif (
                UnleashClient().is_enabled(FeatureFlags.update_contact_webhook) and
                self._need_create_booking(booking, booking_creation_status, webhook_lead.custom_fields)
        ):
            booking: Booking = await self.booking_creation_service(
                webhook_lead=webhook_lead,
                amo_status=booking_creation_status,
                user_id=user.id if user else None,
            )
            # обновляем КАСТОМНЫЕ ПОЛЯ только если создали букинг
            await self._update_booking_custom_fields(booking, webhook_lead)
        elif not booking:
            self.logger.warning('Booking wrong status webhook')
            return

        await self._update_booking_fixation_status(booking, webhook_lead.new_status_id)
        await self._update_booking_status(booking, webhook_lead.new_status_id)

        if booking.user and UnleashClient().is_enabled(FeatureFlags.check_pinning_webhook):
            await self._check_user_pinning_status(booking, webhook_lead, amocrm_substage)

        if not self._is_valid_pipeline(webhook_lead.pipeline_id):
            if booking.active:
                await self.booking_deactivate(booking=booking, data=data)
            return

        await self._update_price_workflow(booking, webhook_lead)
        await self.create_task_instance(booking=booking)

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

    async def _update_booking_fixation_status(self, booking: Booking, new_status_id: int) -> None:
        """
        update booking fixation status
        """
        amocrm_status = await self.amocrm_status_repo.retrieve(
            filters=dict(id=new_status_id),
            related_fields=["group_status"],
        )
        if (
                amocrm_status.group_status
                and amocrm_status.group_status.name not in BOOKING_UPDATE_FIXATION_STATUSES
        ):
            sentry_ctx: dict[str, Any] = dict(
                group_status=amocrm_status.group_status,
                booking=booking,
                new_status_id=new_status_id,
            )
            await send_sentry_log(
                tag="webhook status",
                message="_update_booking_fixation_status",
                context=sentry_ctx,
            )
            await self.update_task_instance_service(
                booking_id=booking.id,
                status_slug=FixationExtensionSlug.DEAL_ALREADY_BOOKED.value,
            )

    async def _update_booking_status(self, booking: Booking, new_status_id: int) -> None:
        """
        update booking status
        """
        skip_statuses = [
            57272745,
            55950761,
            42477951,  # TestStatuses.BOOKING
            # 40127310,  # CallCenterStatuses.BOOKING
            57272765,
            55950773,
            # 50814939,  # EKBStatuses.BOOKING
            # 35065584,  # SPBStatuses.BOOKING
            # 29096401,  # MSKStatuses.BOOKING
            # 21197641,  # TMNStatuses.BOOKING
            37592316,
            39006300,
            33900082,
            # 40127307,  # CallCenterStatuses.MAKE_DECISION  Принимают решение
            # 42477867,  # TestStatuses.MAKE_DECISION
            57272669,
            55950765,
            # 50814933,  # EKBStatuses.MAKE_DECISION
            # 36204954,  # SPBStatuses.MAKE_DECISION
            # 29096398,  # MSKStatuses.MAKE_DECISION
            # 21189712,  # TMNStatuses.MAKE_DECISION
            46323048,
            36829821,
            33900079,
            39006294,
        ]
        sentry_ctx: dict[str, Any] = dict(
            booking=booking,
            new_status_id=new_status_id,
        )

        if new_status_id in skip_statuses and booking.is_agent_assigned():
            sentry_ctx["is_agent_assigned"] = booking.is_agent_assigned()
            sentry_ctx["skip_statuses"] = True
            await send_sentry_log(
                tag="webhook status",
                message="_update_booking_status (1)",
                context=sentry_ctx,
            )
            return

        if new_status_id in ASSIGN_AGENT_STATUSES and booking.is_agent_assigned():
            if booking.amocrm_status_id not in START_STATUSES:
                sentry_ctx["is_agent_assigned"] = booking.is_agent_assigned()
                sentry_ctx["ASSIGN_AGENT_STATUSES"] = False
                await send_sentry_log(
                    tag="webhook status",
                    message="_update_booking_status (2)",
                    context=sentry_ctx,
                )
                return

        status: Optional[AmocrmStatus] = await self.statuses_repo.retrieve(
            filters=dict(id=new_status_id)
        )

        if status and booking:
            sentry_ctx["status"] = status
            await send_sentry_log(
                tag="webhook status",
                message="_update_booking_status (3)",
                context=sentry_ctx,
            )
            data = dict(amocrm_status_id=status.id, amocrm_status=status)
            await self.booking_update(booking=booking, data=data)

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
        data: dict = dict(
            commission=commission,
            commission_value=commission_value,
            tags=tags,
            final_discount=final_discount.value if final_discount else None,
            final_additional_options=final_additional_options.value if final_additional_options else None,
            project=project,
        )
        await self.booking_repo.update(model=booking, data=data)

    async def _check_task_instance_exists(self, booking: Booking) -> bool:
        """
        Проверка наличия задачи для бронирования
        """
        await booking.fetch_related('task_instances')
        if booking.task_instances:
            return True
        return False

    @staticmethod
    def _is_different_amocrm_substage(amocrm_substage, booking) -> bool:
        return amocrm_substage != booking.amocrm_substage

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

        if self._is_different_amocrm_substage(amocrm_substage, booking):
            await self.check_pinning(user_id=booking.user.id)
            return

        if booking.amocrm_status and booking.amocrm_status.pipeline.id != webhook_lead.pipeline_id:
            await self.check_pinning(user_id=booking.user.id)

    async def create_task_instance(self, booking: Booking) -> None:
        """
        Создание задачи для бронирования
        """
        await self.create_task_instance_service(booking_ids=booking.id)
