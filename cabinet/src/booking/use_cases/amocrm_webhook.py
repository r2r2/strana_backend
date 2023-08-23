"""
AMOCRM webhook
"""
import json
import datetime
import structlog
from asyncio import Task
from secrets import compare_digest
from typing import Any, Optional, Type, Union
from urllib.parse import parse_qs, unquote
from pytz import UTC

from fastapi import BackgroundTasks

from common.amocrm import AmoCRM
from common.amocrm.repos import AmoStatusesRepo
from common.email import EmailService
from common.backend.models.amocrm import AmocrmStatus
from src.users.services import ImportContactFromAmoService
from src.properties.repos import Property
from src.task_management.services import CreateTaskInstanceService, UpdateTaskInstanceStatusService
from src.task_management.constants import MeetingsSlug
from src.task_management.utils import check_task_instance_exists
from src.events.repos import CalendarEventRepo
from src.users.repos import UserRepo, User
from src.users.services import CheckPinningStatusService
from src.projects.repos import ProjectRepo, Project
from src.amocrm.repos import AmocrmStatusRepo
from src.meetings.services import CreateRoomService, ImportMeetingFromAmoService
from src.meetings.constants import MeetingType
from src.notifications.services import GetEmailTemplateService
from src.meetings.constants import MeetingStatusChoice
from src.meetings.repos import MeetingRepo, Meeting, MeetingStatusRepo
from ..tasks import activate_bookings_task, deactivate_bookings_task, send_sms_to_msk_client_task
from ..constants import BookingStagesMapping, BookingSubstages
from ..entities import BaseBookingCase
from ..loggers.wrappers import booking_changes_logger
from ..mixins import BookingLogMixin
from ..repos import Booking, BookingRepo, WebhookRequestRepo
from ..types import (
    BookingAmoCRM, BookingPropertyRepo, BookingRequest, CustomFieldValue, WebhookLead
)

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
    meeting_change_status_to_client_mail = "meeting_change_status_to_client_mail"
    meeting_change_status_to_broker_mail = "meeting_change_status_to_broker_mail"

    def __init__(
            self,
            *,
            amocrm_config: dict[str, Any],
            backend_config: dict[str, Any],
            booking_repo: Type[BookingRepo],
            meeting_repo: Type[MeetingRepo],
            meeting_status_repo: Type[MeetingStatusRepo],
            calendar_event_repo: Type[CalendarEventRepo],
            user_repo: Type[UserRepo],
            project_repo: Type[ProjectRepo],
            amocrm_status_repo: Type[AmocrmStatusRepo],
            amocrm_class: Type[BookingAmoCRM],
            request_class: Type[BookingRequest],
            property_repo: Type[BookingPropertyRepo],
            webhook_request_repo: Type[WebhookRequestRepo],
            # fast_booking_webhook_case: BaseBookingCase,
            create_meeting_room_service: CreateRoomService,
            statuses_repo: Type[AmoStatusesRepo],
            background_tasks: BackgroundTasks,
            logger: Optional[Any] = structlog.getLogger(__name__),
            create_booking_log_task: Optional[Any] = None,
            create_task_instance_service: CreateTaskInstanceService,
            update_task_instance_service: UpdateTaskInstanceStatusService,
            check_pinning: CheckPinningStatusService,
            email_class: Type[EmailService],
            get_email_template_service: GetEmailTemplateService,
            import_contact_service: ImportContactFromAmoService,
            import_meeting_service: ImportMeetingFromAmoService,
    ) -> None:
        self.logger = logger
        self.booking_repo: BookingRepo = booking_repo()
        self.meeting_repo: MeetingRepo = meeting_repo()
        self.meeting_status_repo: MeetingStatusRepo = meeting_status_repo()
        self.calendar_event_repo: CalendarEventRepo = calendar_event_repo()
        self.user_repo: UserRepo = user_repo()
        self.project_repo: ProjectRepo = project_repo()
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.property_repo: BookingPropertyRepo = property_repo()
        self.webhook_request_repo: WebhookRequestRepo = webhook_request_repo()
        self.statuses_repo: AmoStatusesRepo = statuses_repo()
        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.request_class: Type[BookingRequest] = request_class
        # self.fast_booking_webhook_case: BaseBookingCase = fast_booking_webhook_case
        self.create_meeting_room_service: CreateRoomService = create_meeting_room_service
        self.background_tasks: BackgroundTasks = background_tasks
        self.create_task_instance_service: CreateTaskInstanceService = create_task_instance_service
        self.update_task_instance_service: UpdateTaskInstanceStatusService = update_task_instance_service
        self.check_pinning: CheckPinningStatusService = check_pinning
        self.email_class: Type[EmailService] = email_class
        self.get_email_template_service: GetEmailTemplateService = get_email_template_service
        self.import_contact_service: ImportContactFromAmoService = import_contact_service
        self.import_meeting_service: ImportMeetingFromAmoService = import_meeting_service

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

    async def __call__(self, secret: str, payload: bytes, *args, **kwargs) -> None:
        data: dict[str, Any] = parse_qs(unquote(payload.decode("utf-8")))
        if not compare_digest(secret, self.secret):
            self.logger.error("Booking resource not found")
            return
        webhook_lead: WebhookLead = self._parse_data(data=data)
        print(webhook_lead.lead_id)
        await self.import_meeting_service(webhook_lead=webhook_lead)
        await self.import_contact_service(webhook_lead=webhook_lead)
        if not webhook_lead.custom_fields:
            self.logger.error("Booking webhook fatal error")
            return

        amocrm_substage: Optional[str] = AmoCRM.get_lead_substage(webhook_lead.new_status_id)

        filters: dict[str, Any] = dict(amocrm_id=webhook_lead.lead_id)
        booking: Optional[Booking] = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["property"],
        )

        if booking:
            filters: dict[str, Any] = dict(
                booking_id=booking.id,
                status__slug__not_in=[MeetingStatusChoice.FINISH, MeetingStatusChoice.CANCELLED],
            )
            meeting = await self.meeting_repo.retrieve(filters=filters)
        else:
            meeting = None

        if not meeting and webhook_lead.custom_fields.get(self.amocrm_class.meeting_type_field_id,
                                                          CustomFieldValue()).value:

            # находим пользователя из сделки вебхука
            user_name = webhook_lead.custom_fields.get(
                self.amocrm_class.meeting_user_name_field_id, CustomFieldValue()
            ).value
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
                project = await self.project_repo.retrieve(filters=dict(amocrm_enum=project_enum))
                if not project:
                    amocrm_status = None
                    booking_amocrm_substage = None
                else:
                    if amocrm_substage == BookingSubstages.MEETING:
                        amocrm_status = await self.amocrm_status_repo.retrieve(
                            filters=dict(
                                pipeline_id=project.amo_pipeline_id,
                                group_status__name__icontains="Встреча назначена",
                            )
                        )
                        booking_amocrm_substage = BookingSubstages.MEETING
                    elif amocrm_substage == BookingSubstages.MEETING_IN_PROGRESS:
                        amocrm_status = await self.amocrm_status_repo.retrieve(
                            filters=dict(
                                pipeline_id=project.amo_pipeline_id,
                                group_status__name__icontains="Идет встреча",
                            )
                        )
                        booking_amocrm_substage = BookingSubstages.MEETING_IN_PROGRESS
                    else:
                        amocrm_status = await self.amocrm_status_repo.retrieve(
                            filters=dict(
                                pipeline_id=project.amo_pipeline_id,
                                group_status__name__icontains="Назначить встречу",
                            )
                        )
                        booking_amocrm_substage = BookingSubstages.MAKE_APPOINTMENT

                if not booking and amocrm_status and booking_amocrm_substage:
                    booking_data = dict(
                        active=True,
                        amocrm_substage=booking_amocrm_substage,
                        project_id=project.id if project else None,
                        amocrm_status_id=amocrm_status.id if amocrm_status else None,
                        amocrm_id=webhook_lead.lead_id,
                        user_id=user.id,
                    )
                    booking = await self.booking_repo.create(booking_data)

                meeting_date: Optional[str] = await self._get_meeting_date(webhook_lead=webhook_lead)
                if booking and meeting_date:
                    await self.create_meeting(
                        webhook_lead=webhook_lead,
                        booking=booking,
                        project=project,
                        meeting_date=meeting_date,
                    )

        amocrm_stage: Optional[str] = BookingStagesMapping()[amocrm_substage]
        property_final_price: Optional[int] = webhook_lead.custom_fields.get(
            self.amocrm_class.property_final_price_field_id, CustomFieldValue()
        ).value
        price_with_sale: Optional[int] = webhook_lead.custom_fields.get(
            self.amocrm_class.property_price_with_sale_field_id, CustomFieldValue()
        ).value

        # ToDo refactoring убрать вместе с self.fast_booking_webhook_case (убрать из /amocrm/notify_contact)
        # Тег "Быстрая бронь" в амо
        # is_fast_lead: bool = self.amocrm_class.fast_booking_tag_id in webhook_lead.tags.keys()
        # fast_booking_data: dict[str, Any] = dict(
        #     amocrm_id=webhook_lead.lead_id,
        #     amocrm_stage=amocrm_stage,
        #     amocrm_substage=amocrm_substage,
        # )

        # if booking and webhook_lead.tags:
            # Есть бронирование и переданы теги
            # fast_booking_data.update(booking=booking)
            # if is_fast_lead and not booking.is_fast_booking():
            #     # Пришел тег "Быстрая бронь" из амо, но в БД бронирование без тега "Быстрая бронь"
            #     booking = await self.fast_booking_webhook_case(**fast_booking_data)
            # else:
            #     # Тег "Быстрая бронь" не пришел из амо, обновляем теги в БД
            #     booking = await self.booking_repo.update(
            #         model=booking, data=dict(
            #             tags=list(webhook_lead.tags.values())
            #         )
            #     )

        # elif is_fast_lead and not booking:
            # Пришел тег "Быстрая бронь" из амо, но в БД нет бронирования
            # booking = await self.fast_booking_webhook_case(**fast_booking_data)

        if not booking:
            return

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
            return

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

        meeting_data = dict()
        if meeting_address := webhook_lead.custom_fields.get(self.amocrm_class.meeting_address_field_id):
            meeting_data.update(meeting_address=meeting_address.value)

        task_instance_created: bool = False
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
            meeting = await self.meeting_repo.retrieve(
                filters=filters,
                related_fields=["booking", "booking__agent", "booking__user", "status", "calendar_event"],
            )

            task_context: dict[str, Any] = dict()
            meeting_date: Optional[str] = await self._get_meeting_date(webhook_lead=webhook_lead)
            if meeting and meeting_date:
                meeting_new_date: datetime = datetime.datetime.fromtimestamp(int(meeting_date), tz=UTC)
                if meeting.date != meeting_new_date:
                    task_context.update(meeting_new_date=meeting_new_date)
                    meeting_data.update(date=meeting_new_date)

            if meeting and amocrm_substage == BookingSubstages.MEETING \
                    and meeting.status.slug == MeetingStatusChoice.NOT_CONFIRM:
                confirm_meeting_status = await self.meeting_status_repo.retrieve(
                    filters=dict(slug=MeetingStatusChoice.CONFIRM)
                )
                meeting_data.update(status_id=confirm_meeting_status.id)
            elif meeting and amocrm_substage == BookingSubstages.MEETING_IN_PROGRESS \
                    and meeting.status.slug == MeetingStatusChoice.CONFIRM:
                start_meeting_status = await self.meeting_status_repo.retrieve(
                    filters=dict(slug=MeetingStatusChoice.START)
                )
                meeting_data.update(status_id=start_meeting_status.id)
                task_context.update(task_status=MeetingsSlug.START.value)
                if meeting.type == MeetingType.ONLINE and not meeting.meeting_link:
                    await self.create_meeting_room_service(
                        unix_datetime=meeting.date.timestamp(),
                        meeting_id=meeting.id,
                    )
            elif meeting and meeting.status.slug == MeetingStatusChoice.START \
                    and booking.amocrm_status_id not in MEETING_IN_PROGRESS_STATUSES:
                finish_meeting_status = await self.meeting_status_repo.retrieve(
                    filters=dict(slug=MeetingStatusChoice.FINISH)
                )
                meeting_data.update(status_id=finish_meeting_status.id)
                task_context.update(task_status=MeetingsSlug.FINISH.value)

            booking: Booking = await self.booking_update(booking=booking, data=data)
            await self.task_created_or_updated(booking=booking, meeting=meeting, task_context=task_context)
            task_instance_created: bool = True
            await self.send_sms_to_msk_client(booking=booking)

        if meeting_data and meeting:
            if meeting.calendar_event and meeting_data.get("date"):
                calendar_event_data = dict(date_start=meeting_data.get("date"))
                await self.calendar_event_repo.update(model=meeting.calendar_event, data=calendar_event_data)

            if meeting:
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

            if not task_instance_created:
                await self.create_task_instance(booking_ids=[booking.id])

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
        tags = json.dumps(list(webhook_lead.tags.values()))
        commission: Optional[int] = custom_fields_dict.get(self.amocrm_class.commission, CustomFieldValue()).value
        commission_value: Optional[int] = custom_fields_dict.get(self.amocrm_class.commission_value,
                                                                 CustomFieldValue()).value
        final_discount = webhook_lead.custom_fields.get(
            self.amocrm_class.booking_final_discount_field_id)
        final_additional_options = webhook_lead.custom_fields.get(
            self.amocrm_class.booking_final_additional_options_field_id)
        data: dict = dict(
            comission=commission,
            comission_value=commission_value,
            tags=tags,
            final_discount=final_discount.value if final_discount else None,
            final_additional_options=final_additional_options.value if final_additional_options else None
        )
        await self.booking_update(booking, data=data)

    async def task_created_or_updated(
        self,
        booking: Booking,
        meeting: Optional[Meeting],
        task_context: dict[str, Any],
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
        task_context: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Создание задачи для бронирования
        """
        await self.create_task_instance_service(booking_ids=booking_ids, task_context=task_context)

    async def update_task_instance(self, booking: Booking, task_context: dict[str, Any]) -> None:
        """
        Обновление задачи для бронирования
        """
        if booking.amocrm_substage == BookingSubstages.MAKE_APPOINTMENT:
            status_slug: str = MeetingsSlug.AWAITING_CONFIRMATION.value

        elif booking.amocrm_substage == BookingSubstages.MEETING:
            if task_context.get("meeting_new_date"):
                status_slug: str = MeetingsSlug.CONFIRMED_RESCHEDULED.value
            else:
                status_slug: str = MeetingsSlug.CONFIRMED.value

        else:
            status_slug: str = task_context.get("task_status", MeetingsSlug.SIGN_UP.value)

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

    async def create_meeting(
        self,
        webhook_lead: WebhookLead,
        booking: Booking,
        project: Project,
        meeting_date: str,
    ) -> None:
        """
        Создание встречи в базе
        """
        confirm_meeting_status = await self.meeting_status_repo.retrieve(
            filters=dict(slug=MeetingStatusChoice.CONFIRM)
        )
        meeting_data: dict = dict(
            booking_id=booking.id,
            city_id=project.city_id if project else None,
            project_id=project.id if project else None,
            date=datetime.datetime.fromtimestamp(
                int(meeting_date),
                tz=UTC,
            ) + datetime.timedelta(hours=2),
            type=self.amocrm_class.meeting_types.get(
                webhook_lead.custom_fields.get(
                    self.amocrm_class.meeting_type_field_id,
                    CustomFieldValue(),
                ).value
            ),
            property_type=self.amocrm_class.meeting_property_types.get(
                webhook_lead.custom_fields.get(
                    self.amocrm_class.meeting_property_type_field_id,
                    CustomFieldValue(),
                ).value
            ),
            status_id=confirm_meeting_status.id,
        )
        await self.meeting_repo.create(data=meeting_data)

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

    async def _get_meeting_date(self, webhook_lead: WebhookLead) -> Optional[str]:
        """
        Получение даты встречи из вебхука
        """
        custom_fields_to_check = [
            self.amocrm_class.meeting_date_zoom_field_id,
            self.amocrm_class.meeting_date_sensei_field_id,
        ]

        for field_id in custom_fields_to_check:
            meeting_date = webhook_lead.custom_fields.get(field_id, CustomFieldValue()).value
            if meeting_date:
                return meeting_date
