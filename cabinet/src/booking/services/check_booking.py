from copy import copy
from asyncio import Task
from datetime import datetime
from typing import Any, Optional, Type, Union

import structlog
from pytz import UTC

from common.email import EmailService
from common.unleash.client import UnleashClient
from config.feature_flags import FeatureFlags
from src.task_management.constants import PaidBookingSlug, OnlineBookingSlug
from src.booking.constants import BookingStages, BookingSubstages, BookingCreatedSources
from src.amocrm.repos import AmocrmStatus, AmocrmStatusRepo
from src.notifications.services import GetEmailTemplateService
from src.properties.constants import PropertyStatuses
from src.payments.repos import PurchaseAmoMatrix, PurchaseAmoMatrixRepo

from ..entities import BaseBookingService
from ..repos import Booking, BookingRepo
from ..types import (
    BookingAmoCRM,
    BookingORM,
    BookingProfitBase,
    BookingPropertyRepo,
    BookingRequest,
)
from ..loggers.wrappers import booking_changes_logger


class CheckBookingService(BaseBookingService):
    """
    Проверка онлайн бронирования
    """
    mail_event_slug = "expired_booking_agent_notification"
    query_type: str = "changePropertyStatus"
    query_name: str = "changePropertyStatus.graphql"
    query_directory: str = "/src/booking/queries/"

    def __init__(
        self,
        backend_config: dict[str, str],
        booking_repo: Type[BookingRepo],
        amocrm_class: Type[BookingAmoCRM],
        request_class: Type[BookingRequest],
        profitbase_class: Type[BookingProfitBase],
        property_repo: Type[BookingPropertyRepo],
        amocrm_status_repo: Type[AmocrmStatusRepo],
        email_class: Type[EmailService],
        update_task_instance_status_service: Any,
        booking_notification_sms_task: Any,
        get_email_template_service: GetEmailTemplateService,
        orm_class: Optional[BookingORM] = None,
        check_booking_task: Optional[Any] = None,
        orm_config: Optional[dict[str, Any]] = None,
        create_booking_log_task: Optional[Any] = None,
        logger: Optional[Any] = structlog.getLogger(__name__),
    ) -> None:
        self.logger = logger
        self.booking_repo: BookingRepo = booking_repo()
        self.property_repo: BookingPropertyRepo = property_repo()
        self.purchase_amo_matrix_repo: PurchaseAmoMatrixRepo = PurchaseAmoMatrixRepo()

        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.request_class: Type[BookingRequest] = request_class
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.email_class: Type[EmailService] = email_class
        self.check_booking_task: Union[Any, None] = check_booking_task
        self.profitbase_class: Type[BookingProfitBase] = profitbase_class
        self.create_booking_log_task: Union[Any, None] = create_booking_log_task
        self.update_task_instance_status_service = update_task_instance_status_service
        self.booking_notification_sms_task: Any = booking_notification_sms_task

        self.login: str = backend_config["internal_login"]
        self.password: str = backend_config["internal_password"]
        self.backend_url: str = backend_config["url"] + backend_config["graphql"]
        self.get_email_template_service: GetEmailTemplateService = (
            get_email_template_service
        )

        self.orm_class: Union[Type[BookingORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

        self.booking_deactivate_for_step_four = booking_changes_logger(
            self.booking_repo.update, self, content="Деактивация бронирования при проверке для ШАГА 4",
        )
        self.booking_deactivate = booking_changes_logger(
            self.booking_repo.update, self, content="Деактивация бронирования при проверке",
        )

    async def __call__(self, booking_id: int, status: Optional[str] = None) -> bool:
        """
        :param status: Статус, устанавливаемый по истечению времени бронирования
        """
        print("CheckBookingService")
        filters: dict[str, Any] = dict(id=booking_id, should_be_deactivated_by_timer=True)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=[
                "user",
                "agent",
                "project__city",
                "property",
                "building",
                "booking_source",
            ],
        )
        print(f'{booking=}')
        if not booking:
            return True

        if booking.step_four():
            print("booking.step_four()")
            data = dict(should_be_deactivated_by_timer=False)
            await self.booking_deactivate_for_step_four(booking=booking, data=data)

            return True
        # elif booking.time_valid():
        #     print("booking.time_valid()")
        #     task_delay: int = (booking.expires - datetime.now(tz=UTC)).seconds
        #     if self.check_booking_task:
        #         pass
        #         # self.check_booking_task.apply_async(
        #         #     (booking.id, status), countdown=task_delay
        #         # )
        #     result: bool = False

        if not status:
            status: str = BookingStages.START

        status_label = BookingSubstages(status).label
        filters = dict(
            name__iexact=status_label,
            pipeline_id=booking.project.amo_pipeline_id,
        )
        actual_amocrm_status: AmocrmStatus = (
            await self.amocrm_status_repo.retrieve(filters=filters)
        )
        data: dict[str, Any] = dict(
            active=False,
            project_id=None,
            property_id=None,
            profitbase_booked=False,
            params_checked=False,
            should_be_deactivated_by_timer=False,
        )
        if self._is_need_to_change_status(booking=booking):
            data["amocrm_stage"] = status
            data["amocrm_substage"] = status
            data["amocrm_status"] = actual_amocrm_status

        if booking.booking_source.slug == BookingCreatedSources.FAST_BOOKING:
            data.pop("property_id")
            data.pop("project_id")
        else:
            await self._process_unbooking(booking, actual_amocrm_status.id)

        self.logger.debug(f"Booking deactivation data: {data}")
        await self.booking_deactivate(booking=booking, data=data)
        property_data: dict[str, Any] = dict(status=PropertyStatuses.FREE)
        await self.property_repo.update(booking.property, data=property_data)
        if booking.booking_source.slug != BookingCreatedSources.FAST_BOOKING:
            await self._backend_unbooking(booking)
        self.booking_notification_sms_task.delay(booking.id)
        await self.update_task_instance_status(booking_id=booking.id)
        return False

    async def _process_unbooking(self, booking: Booking, status_id: int) -> None:
        """
        Обработка отмены бронирования
        """
        if self.__is_strana_lk_3639_enable:
            if booking.is_agent_assigned():
                await self._profitbase_unbooking(booking)
                await self._amocrm_unbooking(booking, status_id)
            elif (
                booking.step_one()
                and not booking.step_two()
                and booking.amocrm_id
            ):
                await self._amocrm_unbooking(booking, status_id)
                await self._send_agent_email(booking=booking)
            elif booking.step_two():
                await self._profitbase_unbooking(booking)
                await self._amocrm_unbooking(booking, status_id)
        else:
            await self._profitbase_unbooking(booking)
            await self._amocrm_unbooking(booking, status_id)

    def _is_need_to_change_status(self, booking: Booking) -> bool:
        match booking.booking_source.slug:
            case BookingCreatedSources.FAST_BOOKING | BookingCreatedSources.LK_ASSIGN:
                # быстрое бронирование
                return False
            case BookingCreatedSources.AMOCRM:
                # бесплатная бронь
                return False
            case _:
                return True

    async def _amocrm_unbooking(self, booking: Booking, status_id: int) -> int:
        """
        Amocrm unbooking
        В АМО сделку в статусе "Бронь" нельзя перевести в статус "Первичный контакт" в кейсе Быстрой брони
        """
        # находим данные из матрицы для поля в амо "Тип оплаты"
        purchase_amo: Optional[PurchaseAmoMatrix] = await self.purchase_amo_matrix_repo.list(
            filters=dict(
                payment_method_id=booking.amo_payment_method_id,
                mortgage_type_id=booking.mortgage_type_id,
            ),
            ordering="priority",
        ).first()
        payment_type_enum: Optional[int] = purchase_amo.amo_payment_type if purchase_amo else None

        async with await self.amocrm_class() as amocrm:
            lead_options: dict[str, Any] = dict(
                status_id=status_id,
                lead_id=booking.amocrm_id,
                city_slug=booking.project.city.slug,
                payment_type_enum=payment_type_enum,
            )
            data: list[Any] = await amocrm.update_lead(**lead_options)
            lead_id: int = data[0]["id"]
        return lead_id

    async def _profitbase_unbooking(self, booking: Booking) -> bool:
        """
        Profitbase unbooking
        """
        async with await self.profitbase_class() as profitbase:
            data: dict[str, bool] = await profitbase.unbook_property(deal_id=booking.amocrm_id)
        success: bool = data["success"]
        return success

    async def _backend_unbooking(self, booking: Booking) -> bool:
        """
        Backend (портал) unbooking
        """
        unbook_options: dict[str, Any] = dict(
            login=self.login,
            url=self.backend_url,
            type=self.query_type,
            password=self.password,
            query_name=self.query_name,
            query_directory=self.query_directory,
            filters=(booking.property.global_id, booking.property.statuses.FREE),
        )
        async with self.request_class(**unbook_options) as response:
            response_ok: bool = response.ok
        return response_ok

    async def _send_agent_email(self, booking: Booking) -> Optional[Task]:
        """
        Уведомление агента об истечении времени на бронирование у клиента по почте
        """
        if not booking.agent:
            return

        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=dict(booking=booking),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic.format(
                    booking_id=booking.id
                ),
                content=email_notification_template.content,
                recipients=[booking.agent.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: Any = self.email_class(**email_options)
            return email_service.as_task()

    async def update_task_instance_status(self, booking_id: int) -> None:
        """
        Обновление статуса задачи
        """
        statuses_to_update: list[str] = [
            PaidBookingSlug.RE_BOOKING.value,
            # OnlineBookingSlug.TIME_IS_UP.value,
        ]
        await self.update_task_instance_status_service(booking_id=booking_id, status_slug=statuses_to_update)

    @property
    def __is_strana_lk_3639_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_3639)
