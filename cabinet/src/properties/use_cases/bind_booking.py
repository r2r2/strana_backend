import asyncio
from asyncio import Task
from typing import Type, Any, Callable, Union, Optional, Awaitable
from datetime import datetime, timedelta

import structlog
from pytz import UTC

from config import booking_config, site_config, MaintenanceSettings, EnvTypes
from common.security import create_access_token
from src.booking.repos import BookingRepo, Booking
from src.booking.services import ActivateBookingService, SendSmsToMskClientService
from src.booking.constants import BookingStages, BookingSubstages, BookingCreatedSources
from src.booking.exceptions import BookingNotFoundError, BookingPropertyUnavailableError, BookingPropertyMissingError
from src.properties.services import CheckProfitbasePropertyService
from src.booking.loggers import booking_changes_logger
from src.booking.types import BookingAmoCRM, BookingEmail, BookingSms
from src.buildings.repos import BuildingBookingTypeRepo, BuildingBookingType
from src.task_management.constants import PaidBookingSlug
from src.task_management.services import UpdateTaskInstanceStatusService
from src.amocrm.repos import AmocrmStatus, AmocrmStatusRepo
from ..entities import BasePropertyCase
from ..exceptions import PropertyNotFoundError
from ..models import RequestBindBookingPropertyModel
from ..repos import Property, PropertyRepo


class BindBookingPropertyCase(BasePropertyCase):
    """
    Создание объекта недвижимости
    """
    AGENT_DISCOUNT: int = 3  # %
    STRANA_OZERNAYA_GLOBALID_DEV: str = "R2xvYmFsUHJvamVjdFR5cGU6c2VyZHRjaGUtc2liaXJp"
    STRANA_OZERNAYA_GLOBALID_PROD: str = "R2xvYmFsUHJvamVjdFR5cGU6c3RyYW5hb3plcm5heWE="
    sms_message_template: str = """
    Агент {agent_full_name} зарезервировал на вас квартиру.
    У вас есть {time_left} на её оплату по ссылке {link}
    """
    lk_client_auth_link_template: str = "https://{site_host}/booking/{booking_id}/{booking_step}?token={token}"
    sms_event_slug = "bind_booking"

    def __init__(
        self,
        property_repo: Type[PropertyRepo],
        booking_repo: Type[BookingRepo],
        building_booking_type_repo: Type[BuildingBookingTypeRepo],
        amocrm_status_repo: Type[AmocrmStatusRepo],
        amocrm_class: Type[BookingAmoCRM],
        activate_bookings_service: ActivateBookingService,
        check_profitbase_property_service: CheckProfitbasePropertyService,
        sms_class: Type[BookingSms],
        email_class: Type[BookingEmail],
        change_booking_status_task: Any,
        update_task_instance_status_service: UpdateTaskInstanceStatusService,
        send_sms_to_msk_client_service: SendSmsToMskClientService,
        global_id_decoder: Callable[[str], tuple[str, Union[str, int]]],
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

        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.activate_bookings_service: ActivateBookingService = activate_bookings_service
        self.token_creator: Callable = create_access_token
        self.check_profitbase_property_service: CheckProfitbasePropertyService = check_profitbase_property_service

        self.change_booking_status_task: Any = change_booking_status_task
        self.update_task_instance_status_service: UpdateTaskInstanceStatusService = update_task_instance_status_service
        self.send_sms_to_msk_client_service: SendSmsToMskClientService = send_sms_to_msk_client_service

        self.site_host: str = site_config["site_host"]
        self.booking_time_hours: int = booking_config["time_hours"]
        self.booking_time_minutes: int = booking_config["time_minutes"]

        self.sms_class: Type[BookingSms] = sms_class
        self.email_class: Type[BookingEmail] = email_class

        self.global_id_decoder: Callable[[str], tuple[str, Union[str, int]]] = global_id_decoder

        self.environment: str = MaintenanceSettings().environment

    async def __call__(self, payload: RequestBindBookingPropertyModel) -> Booking:
        booking_property: Property = await self.property_repo.retrieve(
            filters=dict(id=payload.property_id),
            prefetch_fields=["building", "project"]
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
            filters=booking_filter, prefetch_fields=["property", "building", "agent", "user", "project"]
        )
        if not booking:
            raise BookingNotFoundError

        expires: datetime = datetime.now(tz=UTC) + timedelta(hours=self.booking_time_hours)
        if not booking.is_agent_assigned():
            expires: datetime = datetime.now(tz=UTC) + timedelta(minutes=self.booking_time_minutes)

        filters = dict(
            name__iexact=BookingSubstages.BOOKING_LABEL,
            pipeline_id=booking_property.project.amo_pipeline_id,
        )
        actual_amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(filters=filters)
        self.logger.debug(f"Actual booking status: id={actual_amocrm_status.id} "
                          f"pipeline={actual_amocrm_status.pipeline}")
        booking_data: dict = dict(
            expires=expires,
            property_id=booking_property.id,
            amocrm_stage=BookingStages.BOOKING,
            amocrm_substage=BookingSubstages.BOOKING,
            should_be_deactivated_by_timer=True,
            amocrm_status=actual_amocrm_status,
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

        booking_agent_discount: int = 0
        if booking_property.project.global_id == strana_ozernaya_global_id:
            booking_agent_discount = int(booking_property.original_price * self.AGENT_DISCOUNT / 100)

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

        default_booking_type: BuildingBookingType = await self.building_booking_type_repo.list().first()
        lead_options: dict[str, Any] = dict(
            lead_id=booking.amocrm_id,
            price=booking_property.original_price,
            city_slug=booking_property.project.city,
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
        )
        async with await self.amocrm_class() as amocrm:
            await amocrm.update_lead_v4(**lead_options)

        final_amocrm_substage: str = BookingSubstages.MAKE_DECISION
        await self.activate_bookings_service(booking=booking, amocrm_substage=final_amocrm_substage)
        # дополнительная таска на смену статуса
        # task_delay: int = (booking.expires - datetime.now(tz=UTC)).seconds
        # self.change_booking_status_task.apply_async((booking.id, amocrm_substage), countdown=task_delay)
        return booking

    async def _send_sms(self, booking: Booking) -> Task:
        """
        Отправка SMS о бронировании квартиры клиенту
        """
        token: str = self.token_creator(subject_type=booking.user.type.value, subject=booking.user.id).get("token")
        auth_link_data: dict = dict(
            site_host=self.site_host,
            booking_id=booking.id,
            booking_step=booking.current_step(),
            token=token,
        )
        lk_client_auth_link: str = self.lk_client_auth_link_template.format(**auth_link_data)
        time_difference: timedelta = booking.expires - datetime.now(tz=UTC)
        message_data: dict = dict(
            agent_full_name=booking.agent.full_name,
            time_left=(datetime.min + time_difference).strftime('%H:%M'),
            link=lk_client_auth_link
        )
        message = self.sms_message_template.format(**message_data)

        sms_options: dict[str, Any] = dict(phone=booking.user.phone, message=message, tiny_url=True)
        sms_service: Any = self.sms_class(**sms_options)
        return sms_service.as_task()

    async def update_task_instance_status(self, booking_id: int, status_slug: str) -> None:
        """
        Обновление статуса задачи
        """
        await self.update_task_instance_status_service(booking_id=booking_id, status_slug=status_slug)