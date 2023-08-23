from datetime import datetime
from typing import Callable, NamedTuple, Union
from typing import Type, Optional, Any

import sentry_sdk
from pytz import UTC
import structlog

from common.amocrm.types import AmoLead
from config import backend_config
from src.buildings.repos import BuildingBookingType, BuildingBookingTypeRepo
from ..constants import BookingSubstages
from ..entities import BaseBookingService
from ..exceptions import BookingNotFoundError, BookingPropertyUnavailableError, BookingPropertyMissingError
from ..loggers import booking_changes_logger
from ..mixins import BookingLogMixin
from ..repos import Booking
from ..repos import BookingRepo
from ..types import BookingAmoCRM, BookingProfitBase
from ..types import BookingProperty
from ..types import BookingPropertyRepo, BookingSqlUpdateRequest


class BookingTypeNamedTuple(NamedTuple):
    price: int
    amocrm_id: Optional[int] = None


class ActivateBookingService(BaseBookingService, BookingLogMixin):
    """
    Общий кейс активации бронирования
    """

    query_type: str = "changePropertyStatus"
    query_name: str = "changePropertyStatus.graphql"
    query_directory: str = "/src/booking/queries/"

    def __init__(
        self,
        booking_repo: Type[BookingRepo],
        property_repo: Type[BookingPropertyRepo],
        building_booking_type_repo: Type[BuildingBookingTypeRepo],

        amocrm_class: Type[BookingAmoCRM],
        profitbase_class: Type[BookingProfitBase],
        request_class: Type[BookingSqlUpdateRequest],
        global_id_decoder: Callable[[str], tuple[str, Union[str, int]]],

        check_booking_task: Any,
        create_amocrm_log_task: Any,
        create_booking_log_task: Any,
        booking_notification_sms_task: Any,

        logger: Optional[Any] = structlog.getLogger(__name__),
    ) -> None:
        self.logger = logger
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="АКТИВАЦИЯ БРОНИ | AMOCRM, PORTAL, PROFITBASE"
        )
        self.property_repo: BookingPropertyRepo = property_repo()
        self.request_class: Type[BookingSqlUpdateRequest] = request_class

        self.login: str = backend_config["internal_login"]
        self.password: str = backend_config["internal_password"]
        self.backend_url: str = backend_config["url"] + backend_config["graphql"]
        self.building_booking_type_repo: BuildingBookingTypeRepo = building_booking_type_repo()

        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class
        self.profitbase_class: Type[BookingProfitBase] = profitbase_class
        self.global_id_decoder: Callable[[str], tuple[str, Union[str, int]]] = global_id_decoder
        self.connection_options: dict[str, Any] = dict(
            user=backend_config["db_user"],
            host=backend_config["db_host"],
            port=backend_config["db_port"],
            database=backend_config["db_name"],
            password=backend_config["db_password"],
        )

        self.check_booking_task: Any = check_booking_task
        self.create_amocrm_log_task: Any = create_amocrm_log_task
        self.create_booking_log_task: Any = create_booking_log_task
        self.booking_notification_sms_task: Any = booking_notification_sms_task

    async def __call__(self, booking: Booking, amocrm_substage: str) -> Booking:
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(id=booking.id),
            related_fields=["property", "project", "project__city", "user"]
        )
        data: dict[str] = dict(active=True, should_be_deactivated_by_timer=True)
        booking = await self.booking_update(booking, data=data)
        filters: dict[str] = dict(id=booking.property_id)
        booking_property: BookingProperty = await self.property_repo.retrieve(filters=filters)
        if not booking:
            sentry_sdk.capture_message("cabinet/ActivateBookingService: BookingNotFoundError: No booking")
            raise BookingNotFoundError
        if booking_property:
            self.logger.debug(f"Activate Property data: status={booking_property.status}")
            data: dict[str, Any] = {}
            if booking_property.status in (
                booking_property.statuses.SOLD,
                booking_property.statuses.BOOKED
            ):
                sentry_sdk.capture_message(
                    "cabinet/AcceptContractCase: BookingPropertyMissingError: Неверный статус квартиры"
                )
                raise BookingPropertyMissingError
            data.update(status=booking_property.statuses.BOOKED)
            if amocrm_substage in {BookingSubstages.MONEY_PROCESS, BookingSubstages.REALIZED}:
                data.update(status=booking_property.statuses.SOLD)
            await self.property_repo.update(booking_property, data=data)
            setattr(booking, "property", booking_property)
            await self.__backend_booking(booking=booking)
            if booking.amocrm_id:
                await self.__amocrm_booking(booking=booking)
                await self.__profitbase_booking(booking=booking)

        task_delay: int = (booking.expires - datetime.now(tz=UTC)).seconds
        self.check_booking_task.apply_async((booking.id, amocrm_substage), countdown=task_delay)
        self.booking_notification_sms_task.delay(booking.id)
        self.logger.debug(f"Launch check booking task[celery]: id={booking.id}")

        return booking

    async def __backend_booking(self, booking: Booking) -> str:
        """
        Бронирование в портале
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

    async def __amocrm_booking(self, booking: Booking) -> Optional[int]:
        """
        Бронирование в AmoCRM
        """
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
                    BuildingBookingType,
                    BookingTypeNamedTuple
                ] = await self.building_booking_type_repo.retrieve(
                    filters=booking_type_filter)
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
        async with await self.profitbase_class() as profitbase:
            data: dict[str, bool] = await profitbase.book_property(
                property_id=property_id, deal_id=booking.amocrm_id
            )
            print("Profitbase response", data)
            booked: bool = data.get("success", False)
            in_deal: bool = data.get("code", None) == profitbase.dealed_code
        profitbase_booked: bool = booked or in_deal
        if not profitbase_booked:
            sentry_sdk.capture_message(
                "cabinet/FillPersonalCase: BookingPropertyUnavailableError: not profitbase booked"
            )
            raise BookingPropertyUnavailableError(booked, in_deal)
        return profitbase_booked
