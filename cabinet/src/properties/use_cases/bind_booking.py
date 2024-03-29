import asyncio
import structlog
from asyncio import Task
from pytz import UTC
import json
from typing import Type, Any, Callable, Union, Optional, Awaitable
from datetime import datetime, timedelta

from common.amocrm.types import AmoTag
from common.schemas import UrlEncodeDTO
from common.utils import generate_notify_url
from common.unleash.client import UnleashClient
from config.feature_flags import FeatureFlags
from config import booking_config, site_config, MaintenanceSettings, EnvTypes
from common.security import create_access_token
from src.booking.repos import BookingRepo, Booking
from src.booking.services import ActivateBookingService, SendSmsToMskClientService
from src.booking.constants import BookingStages, BookingSubstages
from src.booking.exceptions import (
    BookingNotFoundError,
    BookingPropertyUnavailableError,
    BookingPropertyMissingError,
)
from src.booking.utils import get_booking_reserv_time
from src.properties.services import CheckProfitbasePropertyService, GetPropertyPriceService
from src.booking.loggers import booking_changes_logger
from src.booking.types import BookingAmoCRM, BookingEmail, BookingSms
from src.buildings.repos import BuildingBookingTypeRepo, BuildingBookingType
from src.task_management.constants import PaidBookingSlug
from src.task_management.dto import CreateTaskDTO
from src.task_management.services import UpdateTaskInstanceStatusService, CreateTaskInstanceService
from src.users.services import CheckPinningStatusServiceV2
from src.amocrm.repos import AmocrmStatus, AmocrmStatusRepo
from src.notifications.services import GetSmsTemplateService
from src.properties.entities import BasePropertyCase
from src.properties.exceptions import PropertyNotFoundError
from src.properties.models import RequestBindBookingPropertyModel
from src.properties.repos import Property, PropertyRepo
from src.payments.repos import PurchaseAmoMatrix, PurchaseAmoMatrixRepo, PropertyPrice


class BindBookingPropertyCase(BasePropertyCase):
    """
    Создание объекта недвижимости [Платная бронь]
    """
    AGENT_DISCOUNT: int = 0  # % скидки для агентов
    STRANA_OZERNAYA_GLOBALID_DEV: str = "R2xvYmFsUHJvamVjdFR5cGU6c2VyZHRjaGUtc2liaXJp"
    STRANA_OZERNAYA_GLOBALID_PROD: str = "R2xvYmFsUHJvamVjdFR5cGU6c3RyYW5hb3plcm5heWE="
    sms_event_slug = "properties_bind"
    lk_client_auth_link_template: str = "/fast-booking"
    aggregator_slug = "aggregator"
    TAG: str = "Бронь от агента"
    AGGREGATOR_TAG: str = "Платная бронь агрегатор"

    def __init__(
        self,
        property_repo: Type[PropertyRepo],
        booking_repo: Type[BookingRepo],
        building_booking_type_repo: Type[BuildingBookingTypeRepo],
        amocrm_status_repo: Type[AmocrmStatusRepo],
        purchase_amo_matrix_repo: Type[PurchaseAmoMatrixRepo],
        amocrm_class: Type[BookingAmoCRM],
        activate_bookings_service: ActivateBookingService,
        check_profitbase_property_service: CheckProfitbasePropertyService,
        sms_class: Type[BookingSms],
        email_class: Type[BookingEmail],
        change_booking_status_task: Any,
        check_booking_task: Any,
        update_task_instance_status_service: UpdateTaskInstanceStatusService,
        create_task_service: CreateTaskInstanceService,
        check_pinning: CheckPinningStatusServiceV2,
        send_sms_to_msk_client_service: SendSmsToMskClientService,
        global_id_decoder: Callable[[str], tuple[str, Union[str, int]]],
        get_sms_template_service: GetSmsTemplateService,
        get_property_price_service: GetPropertyPriceService,
        logger: Optional[Any] = structlog.getLogger(__name__),
    ) -> None:
        self.logger = logger
        self.property_repo: PropertyRepo = property_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="Обновление объекта недвижимости в сделке"
        )
        self.building_booking_type_repo: BuildingBookingTypeRepo = building_booking_type_repo()
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.purchase_amo_matrix_repo: PurchaseAmoMatrixRepo = purchase_amo_matrix_repo()
        self.create_task_service: CreateTaskInstanceService = create_task_service

        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.activate_bookings_service: ActivateBookingService = activate_bookings_service
        self.token_creator: Callable = create_access_token
        self.check_profitbase_property_service: CheckProfitbasePropertyService = check_profitbase_property_service
        self.check_pinning: CheckPinningStatusServiceV2 = check_pinning

        self.change_booking_status_task: Any = change_booking_status_task
        self.check_booking_task: Any = check_booking_task
        self.update_task_instance_status_service: UpdateTaskInstanceStatusService = update_task_instance_status_service
        self.send_sms_to_msk_client_service: SendSmsToMskClientService = send_sms_to_msk_client_service
        self.get_property_price_service: GetPropertyPriceService = get_property_price_service

        self.site_host: str = site_config["site_host"]
        self.booking_time_hours: int = booking_config["time_hours"]
        self.booking_time_minutes: int = booking_config["time_minutes"]

        self.sms_class: Type[BookingSms] = sms_class
        self.email_class: Type[BookingEmail] = email_class

        self.global_id_decoder: Callable[[str], tuple[str, Union[str, int]]] = global_id_decoder

        self.environment: str = MaintenanceSettings().environment

        self.get_sms_template_service: GetSmsTemplateService = get_sms_template_service

    async def __call__(self, payload: RequestBindBookingPropertyModel) -> Booking:
        self.logger.info(f"properties bind payload {payload}")

        booking_property: Property = await self.property_repo.retrieve(
            filters=dict(id=payload.property_id),
            prefetch_fields=["building", "project", "project__city"]
        )
        if not booking_property:
            raise PropertyNotFoundError

        self.logger.debug(f"Booking property: id={booking_property.id} "
                          f"pipeline={booking_property.project.amo_pipeline_id} "
                          f"status={booking_property.status}")

        if booking_property.status in (booking_property.statuses.SOLD, booking_property.statuses.BOOKED):
            raise BookingPropertyMissingError

        property_status, property_available = await self.check_profitbase_property_service(booking_property)
        self.logger.debug(f"Profitbase property data: status={property_status} available={property_available}")
        property_status_bool = property_status == booking_property.statuses.FREE
        if not property_available or not property_status_bool:
            property_data: dict[str, Any] = dict(status=property_status)
            await self.property_repo.update(booking_property, data=property_data)
            raise BookingPropertyUnavailableError(property_status_bool, property_available)

        booking_filter: dict = dict(id=payload.booking_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=booking_filter,
            related_fields=["booking_source"],
            prefetch_fields=["property", "building", "agent", "agency__general_type", "user", "project"]
        )
        if not booking:
            raise BookingNotFoundError

        booking_reserv_time: float = await get_booking_reserv_time(
            created_source=booking.booking_source.slug if booking.booking_source else booking.created_source,
            booking_property=booking_property,
        )

        expires: datetime = datetime.now(tz=UTC) + timedelta(hours=booking_reserv_time)

        filters = dict(
            name__iexact=BookingSubstages.BOOKING_LABEL,
            pipeline_id=booking_property.project.amo_pipeline_id,
        )
        actual_amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(filters=filters)
        self.logger.debug(f"Actual booking status: id={actual_amocrm_status.id} "
                          f"pipeline={actual_amocrm_status.pipeline}")
        if booking.agency and booking.agency.general_type and booking.agency.general_type.slug == self.aggregator_slug:
            tags: list[str] = [self.AGGREGATOR_TAG] + booking.tags if booking.tags else []
        else:
            tags: list[str] = [self.TAG] + booking.tags if booking.tags else []
        booking_data: dict = dict(
            expires=expires,
            property_id=booking_property.id,
            amocrm_stage=BookingStages.BOOKING,
            amocrm_substage=BookingSubstages.BOOKING,
            should_be_deactivated_by_timer=True,
            amocrm_status=actual_amocrm_status,
            tags=tags,
            property_lk=True,
            property_lk_datetime=datetime.now(tz=UTC),
            property_lk_on_time=False,
        )

        building_type: BuildingBookingType = await self.building_booking_type_repo.retrieve(
            filters=dict(id=payload.booking_type_id)
        )
        self.logger.debug(f"Bind booking type: {building_type}")
        if building_type:
            booking_data.update(
                payment_amount=building_type.price,
                booking_period=building_type.period,
                until=datetime.now(tz=UTC) + timedelta(days=building_type.period),
            )

        strana_ozernaya_global_id: str = ""
        if self.environment in (EnvTypes.STAGE, EnvTypes.DEV):
            strana_ozernaya_global_id = self.STRANA_OZERNAYA_GLOBALID_DEV
        elif self.environment == EnvTypes.PROD:
            strana_ozernaya_global_id = self.STRANA_OZERNAYA_GLOBALID_PROD

        booking_discount: int = booking_property.building.discount
        if not booking_discount:
            booking_discount: int = booking_property.project.discount
        if booking_property.project.global_id == strana_ozernaya_global_id:
            booking_discount: int = self.AGENT_DISCOUNT

        booking_agent_discount: int = int(booking_property.original_price * booking_discount / 100)

        if building := booking_property.building:
            additional_data: dict = dict(
                floor_id=booking_property.floor_id,
                project_id=booking_property.project_id,
                building_id=booking_property.building_id,
                final_payment_amount=int(booking_property.original_price - booking_agent_discount),
                start_commission=building.default_commission,
                commission=building.default_commission,
            )
            booking_data.update(additional_data)

        self.logger.info(f"{payload.payment_method_slug=}")
        self.logger.info(f"{payload.mortgage_type_by_dev=}")
        self.logger.info(f"{payload.mortgage_program_name=}")
        self.logger.info(f"{payload.calculator_options=}")

        booking_data.update(mortgage_offer=payload.mortgage_program_name)
        try:
            json.loads(payload.calculator_options)  # проверяем, что текст совместим с json
            booking_data.update(calculator_options=payload.calculator_options)
        except Exception:
            self.logger.error(
                f"В поле опции калькулятора передан не json-совместимый текст - {payload.calculator_options=}"
            )

        if payload.payment_method_slug:
            booking_property_price, price_offer_matrix = await self.get_property_price_service(
                property_id=booking_property.id,
                property_payment_method_slug=payload.payment_method_slug,
                property_mortgage_type_by_dev=payload.mortgage_type_by_dev,
            )
            if booking_property_price and price_offer_matrix:
                booking_agent_discount: int = int(booking_property_price.price * booking_discount / 100)
                booking_data.update(
                    price_id=booking_property_price.id,
                    amo_payment_method_id=price_offer_matrix.payment_method_id,
                    mortgage_type_id=price_offer_matrix.mortgage_type_id,
                    price_offer_id=price_offer_matrix.id,
                    final_payment_amount=int(booking_property_price.price - booking_agent_discount),
                )

        booking: Booking = await self.booking_update(booking=booking, data=booking_data)
        if booking.is_agent_assigned():
            asyncio_tasks: list[Awaitable] = [
                self.update_task_instance_status(
                    booking_id=booking.id,
                    status_slug=PaidBookingSlug.WAIT_PAYMENT.value,
                )
            ]
            if not booking.user.sms_send:
                asyncio_tasks.append(
                    self.send_sms_to_msk_client_service(booking_id=booking.id, sms_slug=self.sms_event_slug)
                )
            asyncio_tasks.append(self._send_sms(booking))
            await asyncio.gather(*asyncio_tasks)

        booking_property: Property = await self.property_repo.retrieve(
            filters=dict(id=payload.property_id),
            prefetch_fields=["building", "project", "project__city"]
        )

        # находим данные из матрицы для поля в амо "Тип оплаты"
        purchase_amo: Optional[PurchaseAmoMatrix] = await self.purchase_amo_matrix_repo.list(
            filters=dict(
                payment_method_id=booking.amo_payment_method_id,
                mortgage_type_id=booking.mortgage_type_id,
            ),
            ordering="priority",
        ).first()
        payment_type_enum: Optional[int] = purchase_amo.amo_payment_type if purchase_amo else None

        tags: list[AmoTag] = [AmoTag(name=tag) for tag in tags]
        default_booking_type: BuildingBookingType = await self.building_booking_type_repo.list().first()
        lead_options: dict[str, Any] = dict(
            lead_id=booking.amocrm_id,
            price=booking_property.original_price,
            city_slug=booking_property.project.city.slug,
            status_id=actual_amocrm_status.id,
            property_id=self.global_id_decoder(booking_property.global_id)[1],
            property_type=booking_property.type.value.lower(),
            booking_type_id=building_type.amocrm_id if building_type else default_booking_type.amocrm_id,
            booking_discount=booking_agent_discount,
            price_with_sales=booking.final_payment_amount,
            project_amocrm_name=booking_property.project.amocrm_name,
            project_amocrm_enum=booking_property.project.amocrm_enum,
            project_amocrm_pipeline_id=booking_property.project.amo_pipeline_id,
            project_amocrm_organization=booking_property.project.amocrm_organization,
            project_amocrm_responsible_user_id=booking_property.project.amo_responsible_user_id,
            payment_type_enum=payment_type_enum,
            tags=tags,
        )
        async with await self.amocrm_class() as amocrm:
            await amocrm.update_lead_v4(**lead_options)
            if calculator_options_data := booking_data.get("calculator_options"):
                await amocrm.send_lead_note(
                    lead_id=booking.amocrm_id,
                    message=f"Выбранные опции - {calculator_options_data}",
                )
            if mortgage_offer_data := booking_data.get('mortgage_offer'):
                await amocrm.send_lead_note(
                    lead_id=booking.amocrm_id,
                    message=f"Название ипотечной программы - {mortgage_offer_data}",
                )

        final_amocrm_substage: str = BookingSubstages.MAKE_DECISION
        await self.activate_bookings_service(booking=booking, amocrm_substage=final_amocrm_substage)
        # дополнительная таска на смену статуса
        # task_delay: int = (booking.expires - datetime.now(tz=UTC)).seconds
        # self.change_booking_status_task.apply_async((booking.id, amocrm_substage), countdown=task_delay)
        self.check_booking_task.apply_async((booking.id,), eta=booking.expires, queue="scheduled")
        self.check_pinning.as_task(user_id=booking.user.id)
        await self._create_task_instance(booking=booking)
        return booking

    async def _send_sms(self, booking: Booking) -> Task:
        """
        Отправка SMS о бронировании квартиры клиенту
        """
        sms_notification_template = await self.get_sms_template_service(
            sms_event_slug=self.sms_event_slug,
        )

        if sms_notification_template and sms_notification_template.is_active:
            token: str = self.token_creator(subject_type=booking.user.type.value, subject=booking.user.id).get("token")
            query_params: dict[str, Any] = dict(
                bookingId=booking.id,
                token=token,
            )
            data: dict[str, Any] = dict(
                route_template=self.lk_client_auth_link_template,
                host=self.site_host,
                query_params=query_params,
                use_ampersand_ascii=True,
            )
            url_dto: UrlEncodeDTO = UrlEncodeDTO(**data)
            fast_booking_link: str = generate_notify_url(url_dto=url_dto)

            time_difference: timedelta = booking.expires - datetime.now(tz=UTC)
            message_data: dict = dict(
                agent_full_name=booking.agent.full_name,
                time_left=(datetime.min + time_difference).strftime('%H:%M'),
                link=fast_booking_link,
            )
            message = sms_notification_template.template_text.format(**message_data)

            sms_options: dict[str, Any] = dict(
                message=message,
                phone=booking.user.phone,
                tiny_url=True,
                lk_type=sms_notification_template.lk_type.value,
                sms_event_slug=sms_notification_template.sms_event_slug,
            )

            sms_service: Any = self.sms_class(**sms_options)
            return sms_service.as_task()

    async def update_task_instance_status(self, booking_id: int, status_slug: str) -> None:
        """
        Обновление статуса задачи
        """
        await self.update_task_instance_status_service(booking_id=booking_id, status_slug=status_slug)

    async def _create_task_instance(self, booking: Booking) -> None:
        """
        Создание задачи
        """
        task_context: CreateTaskDTO = CreateTaskDTO()
        task_context.is_main = True
        await self.create_task_service(booking_ids=booking.id, task_context=task_context)
