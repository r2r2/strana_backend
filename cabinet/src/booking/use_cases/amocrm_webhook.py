"""
AMOCRM webhook
"""
from secrets import compare_digest
from typing import Any, Optional, Type, Union
from urllib.parse import parse_qs, unquote
import datetime
from pytz import UTC

import structlog
from common.amocrm import AmoCRM
from common.amocrm.repos import AmoStatusesRepo
from common.backend.models.amocrm import AmocrmStatus
from fastapi import BackgroundTasks

from ..constants import BookingStagesMapping, BookingSubstages
from ..entities import BaseBookingCase
from ..loggers.wrappers import booking_changes_logger
from ..mixins import BookingLogMixin
from ..repos import Booking, BookingRepo, WebhookRequestRepo
from ..tasks import activate_bookings_task, deactivate_bookings_task, send_sms_to_msk_client_task
from src.properties.repos import Property
from src.task_management.services import CreateTaskInstanceService
from src.users.repos import UserRepo
from src.users.services import CheckPinningStatusService
from src.projects.repos import ProjectRepo
from src.amocrm.repos import AmocrmStatusRepo
from src.meetings.services import CreateRoomService
from src.meetings.constants import MeetingType
from ..types import (BookingAmoCRM, BookingPropertyRepo, BookingRequest,
                     CustomFieldValue, WebhookLead)
from ...meetings.constants import MeetingStatus
from ...meetings.repos import MeetingRepo

MEETING_IN_PROGRESS_STATUSES = [
    AmoCRM.TMNStatuses.MEETING_IN_PROGRESS,
    AmoCRM.MSKStatuses.MEETING_IN_PROGRESS,
    AmoCRM.SPBStatuses.MEETING_IN_PROGRESS,
    AmoCRM.EKBStatuses.MEETING_IN_PROGRESS,
]


class AmoCRMWebhookCase(BaseBookingCase, BookingLogMixin):
    """
    Вебхук АМО
    """

    query_type: str = "changePropertyStatus"
    query_name: str = "changePropertyStatus.graphql"
    query_directory: str = "/src/booking/queries/"
    actions: list[str] = ["add", "status", "update", "create"]

    def __init__(
        self,
        *,
        amocrm_config: dict[str, Any],
        backend_config: dict[str, Any],
        booking_repo: Type[BookingRepo],
        meeting_repo: Type[MeetingRepo],
        user_repo: Type[UserRepo],
        project_repo: Type[ProjectRepo],
        amocrm_status_repo: Type[AmocrmStatusRepo],
        amocrm_class: Type[BookingAmoCRM],
        request_class: Type[BookingRequest],
        property_repo: Type[BookingPropertyRepo],
        webhook_request_repo: Type[WebhookRequestRepo],
        fast_booking_webhook_case: BaseBookingCase,
        create_meeting_room_service: CreateRoomService,
        statuses_repo: Type[AmoStatusesRepo],
        background_tasks: BackgroundTasks,
        logger: Optional[Any] = structlog.getLogger(__name__),
        create_booking_log_task: Optional[Any] = None,
        create_task_instance_service: CreateTaskInstanceService,
        check_pinning: CheckPinningStatusService,
    ) -> None:
        self.logger = logger
        self.booking_repo: BookingRepo = booking_repo()
        self.meeting_repo: MeetingRepo = meeting_repo()
        self.user_repo: UserRepo = user_repo()
        self.project_repo: ProjectRepo = project_repo()
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.property_repo: BookingPropertyRepo = property_repo()
        self.webhook_request_repo: WebhookRequestRepo = webhook_request_repo()
        self.statuses_repo: AmoStatusesRepo = statuses_repo()
        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.request_class: Type[BookingRequest] = request_class
        self.fast_booking_webhook_case: BaseBookingCase = fast_booking_webhook_case
        self.create_meeting_room_service: CreateRoomService = create_meeting_room_service
        self.background_tasks: BackgroundTasks = background_tasks
        self.create_task_instance_service: CreateTaskInstanceService = create_task_instance_service
        self.check_pinning: CheckPinningStatusService = check_pinning

        self.secret: str = amocrm_config["secret"]
        self.login: str = backend_config["internal_login"]
        self.password: str = backend_config["internal_password"]
        self.backend_url: str = backend_config["url"] + backend_config["graphql"]

        self.create_booking_log_task: Any = create_booking_log_task
        self.booking_update = booking_changes_logger(self.booking_repo.update, self, content="Изменение статуса "
                                                                                             "webhook | AMOCRM")
        self.booking_deactivate = booking_changes_logger(self.booking_repo.update, self, content="Деактивация брони "
                                                                                                 "webhook воронка не "
                                                                                                 "поддерживается | "
                                                                                                 "AMOCRM")

    async def __call__(self, secret: str, payload: bytes, *args, **kwargs) -> Optional[Booking]:
        data: dict[str, Any] = parse_qs(unquote(payload.decode("utf-8")))

        if not compare_digest(secret, self.secret):
            self.logger.error("Booking resource not found")
            return None

        webhook_lead: WebhookLead = self._parse_data(data=data)
        if not webhook_lead.custom_fields:
            self.logger.error("Booking webhook fatal error")
            return None

        filters: dict[str, Any] = dict(amocrm_id=webhook_lead.lead_id)
        booking: Optional[Booking] = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["property"],
        )

        if booking:
            filters: dict[str, Any] = dict(booking_id=booking.id)
            meeting = await self.meeting_repo.retrieve(filters=filters)
        else:
            meeting = None

        if not meeting and webhook_lead.custom_fields.get(self.amocrm_class.meeting_type_field_id,
                                                         CustomFieldValue()).value:

            # находим пользователя из сделки вебхука
            user_name = webhook_lead.custom_fields.get(self.amocrm_class.meeting_user_name_id, CustomFieldValue()).value
            if not user_name:
                user = None
            else:
                user_name = user_name.split()
                if len(user_name) == 3:
                    user = await self.user_repo.retrieve(filters=dict(
                        surname__icontains=user_name[0],
                        name__icontains=user_name[1],
                        patronymic__icontains=user_name[2],
                    ))
                elif len(user_name) == 2:
                    user = await self.user_repo.retrieve(filters=dict(
                        surname__icontains=user_name[0],
                        name__icontains=user_name[1],
                    ))
                else:
                    user = None

            # создаем сделку в БД для сделки вебхука встречи из амо
            if user:
                # находим проект из сделки вебхука
                project_enum = webhook_lead.custom_fields.get(self.amocrm_class.project_field_id,
                                                              CustomFieldValue()).value
                if not project_enum:
                    project = None
                    amocrm_status = None
                else:
                    project = await self.project_repo.retrieve(filters=dict(amocrm_enum=project_enum))
                    if project:
                        amocrm_status = await self.amocrm_status_repo.retrieve(
                            filters=dict(
                                pipeline_id=project.amo_pipeline_id,
                                name__icontains="Назначить встречу",
                            )
                        )
                    else:
                        amocrm_status = None

                if not booking:
                    booking_data = dict(
                        active=True,
                        amocrm_substage=BookingSubstages.MAKE_APPOINTMENT,
                        project_id=project.id if project else None,
                        amocrm_status_id=amocrm_status.id if amocrm_status else None,
                        amocrm_id=webhook_lead.lead_id,
                        user_id=user.id,
                    )
                    booking = await self.booking_repo.create(booking_data)

                meeting_data: dict = dict(
                    booking_id=booking.id,
                    city_id=project.city_id if project else None,
                    project_id=project.id if project else None,
                    date=datetime.datetime.fromtimestamp(
                        int(webhook_lead.custom_fields.get(self.amocrm_class.meeting_date_id).value),
                        tz=UTC,
                    ) + datetime.timedelta(hours=2),
                    type=self.amocrm_class.meeting_types.get(
                        webhook_lead.custom_fields.get(self.amocrm_class.meeting_type_field_id).value
                    ),
                    property_type=self.amocrm_class.meeting_property_types.get(
                        webhook_lead.custom_fields.get(self.amocrm_class.meeting_property_type_id).value
                    ),
                    status=MeetingStatus.CONFIRM,
                )
                await self.meeting_repo.create(data=meeting_data)

        amocrm_substage: Optional[str] = AmoCRM.get_lead_substage(webhook_lead.new_status_id)
        amocrm_stage: Optional[str] = BookingStagesMapping()[amocrm_substage]
        property_final_price: Optional[int] = webhook_lead.custom_fields.get(
            self.amocrm_class.property_final_price_field_id, CustomFieldValue()
        ).value
        price_with_sale: Optional[int] = webhook_lead.custom_fields.get(
            self.amocrm_class.property_price_with_sale_field_id, CustomFieldValue()
        ).value

        # Тег "Быстрая бронь" в амо
        is_fast_lead: bool = self.amocrm_class.fast_booking_tag_id in webhook_lead.tags.keys()
        fast_booking_data: dict[str, Any] = dict(
            booking=booking,
            webhook_lead=webhook_lead,
            amocrm_stage=amocrm_stage,
            amocrm_substage=amocrm_substage,
        )

        if booking and webhook_lead.tags:
            # Есть бронирование и переданы теги
            if is_fast_lead and not booking.is_fast_booking():
                # Пришел тег "Быстрая бронь" из амо, но в БД бронирование без тега "Быстрая бронь"
                booking = await self.fast_booking_webhook_case(**fast_booking_data)
            else:
                # Тег "Быстрая бронь" не пришел из амо, обновляем теги в БД
                await self.booking_update(booking=booking, data=dict(tags=list(webhook_lead.tags.values())))

        elif is_fast_lead and not booking:
            # Пришел тег "Быстрая бронь" из амо, но в БД нет бронирования
            booking = await self.fast_booking_webhook_case(**fast_booking_data)

        if not booking:
            return None

        await self._update_booking_status(booking, webhook_lead.new_status_id)
        await self._update_booking_custom_fields(booking, webhook_lead)
        if booking.user:
            await self._check_user_pinning_status(booking, webhook_lead, amocrm_substage)

        # Не обновляем сделки из воронок, кроме городов
        if webhook_lead.pipeline_id not in self.amocrm_class.sales_pipeline_ids:
            if booking.active:
                await self.booking_deactivate(booking=booking, data=data)
            self.logger.warning(
                'Booking wrong pipeline',
                pipeline_id=webhook_lead.pipeline_id,
                lead_id=webhook_lead.lead_id,
            )
            return None

        has_property: bool = False
        stages_valid = self._is_stage_valid(amocrm_substage=amocrm_substage)
        if webhook_lead.custom_fields.get(self.amocrm_class.property_field_id, CustomFieldValue()).value:
            has_property: bool = True
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

        if property_final_price or price_with_sale:
            data = dict(final_payment_amount=property_final_price or price_with_sale)
            booking: Booking = await self.booking_update(booking=booking, data=data)
            property: Property = await self.property_repo.retrieve(filters=dict(id=booking.property_id))
            if property:
                data = dict(final_price=price_with_sale or property_final_price)
                await self.property_repo.update(model=property, data=data)

        if amocrm_substage != booking.amocrm_substage:
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
            filters: dict[str, Any] = dict(booking_id=booking.id)
            meeting = await self.meeting_repo.retrieve(filters=filters)

            if meeting and amocrm_substage == BookingSubstages.MEETING and meeting.status == MeetingStatus.NOT_CONFIRM:
                meeting_data = dict(status=MeetingStatus.CONFIRM)
                await self.meeting_repo.update(model=meeting, data=meeting_data)
            elif meeting and amocrm_substage == BookingSubstages.MEETING_IN_PROGRESS \
                    and meeting.status == MeetingStatus.CONFIRM:
                meeting_data = dict(status=MeetingStatus.START)
                await self.meeting_repo.update(model=meeting, data=meeting_data)
                if meeting.type == MeetingType.ONLINE and not meeting.meeting_link:
                    await self.create_meeting_room_service(
                        unix_datetime=meeting.date.timestamp(),
                        meeting_id=meeting.id,
                    )
            elif meeting and meeting.status == MeetingStatus.START \
                    and booking.amocrm_status_id not in MEETING_IN_PROGRESS_STATUSES:
                meeting_data = dict(status=MeetingStatus.FINISH)
                await self.meeting_repo.update(model=meeting, data=meeting_data)
            booking: Booking = await self.booking_update(booking=booking, data=data)
            await self.create_task_instance(booking_ids=[booking.id])
            await self.send_sms_to_msk_client(booking=booking)
        return booking

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

    async def _update_booking_status(self, booking: Booking, new_status_id: int):
        """
        update booking status
        """
        if new_status_id in [57272745, 55950761, 51944400, 51489690, 51105825, 41481162,
                             50284815, 42477951, 40127310, 57272765, 55950773, 50814939,
                             35065584, 29096401, 21197641, 37592316, 39006300, 33900082,
                             40127307, 42477867, 57272669, 55950765, 50814933, 36204954,
                             29096398, 21189712, 46323048, 36829821, 33900079, 39006294] \
                and booking.is_agent_assigned():
            return
        status: Optional[AmocrmStatus] = await self.statuses_repo.retrieve(
            filters=dict(id=new_status_id)
        )
        if status:
            data = dict(amocrm_status_id=status.id, amocrm_status=status)
            await self.booking_update(booking=booking, data=data)

    async def _update_booking_custom_fields(self, booking: Booking, webhook_lead: WebhookLead):
        """
        update booking custom fields
        """
        custom_fields_dict = webhook_lead.custom_fields
        tags = webhook_lead.tags.values()
        commission: Optional[int] = custom_fields_dict.get(self.amocrm_class.commission, CustomFieldValue()).value
        commission_value: Optional[int] = custom_fields_dict.get(self.amocrm_class.commission_value,
                                                                 CustomFieldValue()).value
        data: dict = dict(
            comission=commission,
            comission_value=commission_value,
            tags=tags,
        )
        await self.booking_update(booking, data=data)

    async def create_task_instance(self, booking_ids: list[int]) -> None:
        """
        Создание задачи для бронирования
        """
        await self.create_task_instance_service(booking_ids=booking_ids)

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
            self.check_pinning.as_task(user_id=booking.user.id)
            return

        if booking.amocrm_status:
            if booking.amocrm_status.pipeline.id != webhook_lead.pipeline_id:
                self.check_pinning.as_task(user_id=booking.user.id)

    async def send_sms_to_msk_client(self, booking: Booking) -> None:
        """
        Отправка смс клиенту из МСК
        """
        if booking.substages != BookingSubstages.BOOKING or not booking.user:
            # Отправляем СМС только в статусе БРОНЬ
            return
        sms_slug: str = "assign_client"
        send_sms_to_msk_client_task.delay(booking_id=booking.id, sms_slug=sms_slug)
