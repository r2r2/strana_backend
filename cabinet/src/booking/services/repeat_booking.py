from datetime import datetime
from typing import Callable, Union, Type, Any, Optional

from pytz import UTC

from src.buildings.repos import BuildingBookingType, BuildingBookingTypeRepo
from ..constants import BookingSubstages, BookingTypeNamedTuple
from ..entities import BaseBookingService
from ..exceptions import BookingPropertyUnavailableError, BookingPropertyMissingError
from ..loggers import booking_changes_logger
from ..repos import Booking, BookingRepo
from ..types import (
    BookingAmoCRM, BookingProfitBase, BookingProperty, BookingPropertyRepo, BookingSqlUpdateRequest
)
from common.amocrm.types import AmoLead
from config import backend_config
from ...task_management.constants import PaidBookingSlug


class RepeatBookingService(BaseBookingService):
    """
    Кейс повторной активации бронирования
    """
    def __init__(
            self,
            booking_repo: Type[BookingRepo],
            property_repo: Type[BookingPropertyRepo],
            check_booking_task: Any,
            global_id_decoder: Callable[[str], tuple[str, Union[str, int]]],
            request_class: Type[BookingSqlUpdateRequest],
            amocrm_class: Type[BookingAmoCRM],
            building_booking_type_repo: Type[BuildingBookingTypeRepo],
            create_amocrm_log_task: Any,
            update_task_instance_status_task: Any,
            profitbase_class: Type[BookingProfitBase],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="ПОВТОРНАЯ АКТИВАЦИЯ БРОНИ | AMOCRM, PORTAL, PROFITBASE"
        )
        self.property_repo: BookingPropertyRepo = property_repo()
        self.check_booking_task: Any = check_booking_task
        self.update_task_instance_status_task: Any = update_task_instance_status_task
        self.global_id_decoder: Callable[[str], tuple[str, Union[str, int]]] = global_id_decoder
        self.request_class: Type[BookingSqlUpdateRequest] = request_class
        self.building_booking_type_repo: BuildingBookingTypeRepo = building_booking_type_repo()
        self.create_amocrm_log_task: Any = create_amocrm_log_task
        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.profitbase_class: Type[BookingProfitBase] = profitbase_class
        self.connection_options: dict[str, Any] = dict(
            user=backend_config["db_user"],
            host=backend_config["db_host"],
            port=backend_config["db_port"],
            database=backend_config["db_name"],
            password=backend_config["db_password"],
        )

    async def __call__(
            self,
            booking: Booking,
            expires: datetime,
            amocrm_substage: Optional[str] = BookingSubstages.BOOKING
    ) -> Booking:
        activate_booking_data: dict = dict(
            active=True,
            should_be_deactivated_by_timer=True,
            amocrm_substage=amocrm_substage,
            expires=expires
        )

        property_filters: dict = dict(id=booking.property.id)
        booking_property: BookingProperty = await self.property_repo.retrieve(filters=property_filters)
        if not booking_property:
            raise BookingPropertyMissingError

        await self.__backend_booking(booking=booking)
        await self.__amocrm_booking(booking=booking)
        await self.__profitbase_booking(booking=booking)

        activated_booking: Booking = await self.booking_update(booking, data=activate_booking_data)
        task_delay: int = (activated_booking.expires - datetime.now(tz=UTC)).seconds
        self.check_booking_task.apply_async((activated_booking.id,), countdown=task_delay)
        self.update_task_instance_status_task.delay(
            booking_id=booking.id,
            status_slug=PaidBookingSlug.WAIT_PAYMENT.value,
        )

        return activated_booking

    async def __backend_booking(self, booking: Booking) -> str:
        """
        Бронирование на портале
        """
        property_id = self.global_id_decoder(booking.property.global_id)[1]
        request_options: dict[str, Any] = dict(
            table="properties_property",
            filters=dict(id=property_id),
            data=dict(status=booking.property.statuses.BOOKED),
            connection_options=self.connection_options,
        )
        async with self.request_class(**request_options) as response:
            result: str = response
        return result

    async def __amocrm_booking(self, booking: Booking) -> int:
        """
        Бронирование в AmoCRM
        """
        await booking.fetch_related("project", "project__city")
        async with await self.amocrm_class() as amocrm:
            lead_options: dict[str, Any] = dict(lead_id=booking.amocrm_id)
            lead: list[Any] = await amocrm.fetch_lead(**lead_options)

            if lead:
                lead_options: dict[str, Any] = dict(
                    status=BookingSubstages.BOOKING,
                    lead_id=booking.amocrm_id,
                    city_slug=booking.project.city.slug,
                )
                data: list[Any] = await amocrm.update_lead(**lead_options)
                lead_id: int = data[0]["id"]
            else:
                booking_type_filter = dict(period=booking.booking_period, price=booking.payment_amount)
                booking_type: Union[
                    BuildingBookingType, BookingTypeNamedTuple
                ] = await self.building_booking_type_repo.retrieve(filters=booking_type_filter)
                if not booking_type:
                    booking_type = BookingTypeNamedTuple(price=int(booking.payment_amount))

                lead_options: dict[str, Any] = dict(
                    status=BookingSubstages.START,
                    tags=booking.tags,
                    city_slug=booking.project.city.slug,
                    property_type=booking.property.type.value.lower(),
                    user_amocrm_id=booking.user.amocrm_id,
                    project_amocrm_name=booking.project.amocrm_name,
                    project_amocrm_enum=booking.project.amocrm_enum,
                    project_amocrm_organization=booking.project.amocrm_organization,
                    project_amocrm_pipeline_id=booking.project.amo_pipeline_id,
                    project_amocrm_responsible_user_id=booking.project.amo_responsible_user_id,
                    property_id=self.global_id_decoder(booking.property.global_id)[1],
                    booking_type_id=booking_type.amocrm_id,
                    creator_user_id=booking.user.id,
                )

                data: list[AmoLead] = await amocrm.create_lead(**lead_options)
                lead_id: int = data[0].id
                note_data: dict[str, Any] = dict(
                    element="lead",
                    lead_id=lead_id,
                    note="lead_created",
                    text="Создано онлайн-бронирование",
                )
                self.create_amocrm_log_task.delay(note_data=note_data)
                lead_options: dict[str, Any] = dict(
                    status=BookingSubstages.BOOKING, lead_id=lead_id, city_slug=booking.project.city.slug
                )
                data: list[Any] = await amocrm.update_lead(**lead_options)
                lead_id: int = data[0]["id"]
                note_data: dict[str, Any] = dict(
                    element="lead",
                    lead_id=lead_id,
                    note="lead_changed",
                    text="Изменен статус заявки на 'Бронь'",
                )
                self.create_amocrm_log_task.delay(note_data=note_data)
        return lead_id

    async def __profitbase_booking(self, booking: Booking) -> bool:
        """
        Бронированиве в profitbase
        """
        property_id: int = self.global_id_decoder(booking.property.global_id)[1]
        async with await self.profitbase_class() as profit_base:
            data: dict[str, bool] = await profit_base.book_property(
                property_id=property_id, deal_id=booking.amocrm_id
            )
            booked: bool = data.get("success", False)
            in_deal: bool = data.get("code", None) == profit_base.dealed_code
        profitbase_booked: bool = booked or in_deal
        if not profitbase_booked:
            raise BookingPropertyUnavailableError(booked, in_deal)
        return profitbase_booked
