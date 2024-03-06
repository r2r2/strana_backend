import datetime
from typing import Any, Callable, Type

import structlog
from pytz import UTC

from common import amocrm
from common.amocrm.exceptions import AmoFetchLeadNotFoundError
from common.amocrm.types import AmoLead
from src.properties.services import CheckProfitbasePropertyService
from ..constants import (FORBIDDEN_FOR_BOOKING_PROPERTY_PARAMS,
                         BookingSubstages)
from ..entities import BaseBookingCase
from src.booking.exceptions import (
    BookingForbiddenError,
    BookingPropertyMissingError,
    BookingNotFoundError,
    BookingUnfinishedExistsError,
    BookingPropertyAlreadyBookedError,
)
from ..loggers import booking_changes_logger
from ..mixins import BookingLogMixin
from ..repos import Booking, BookingRepo
from ..services import ActivateBookingService
from ..types import BookingPropertyRepo
from src.properties.repos import Property
from src.task_management.constants import OnlineBookingSlug, FastBookingSlug, FreeBookingSlug
from src.task_management.utils import get_booking_tasks


class BookingRepeat(BaseBookingCase, BookingLogMixin):
    def __init__(
        self,
        check_booking_task: Any,
        create_booking_log_task: Any,
        booking_config: dict[str, Any],
        backend_config: dict[str, Any],
        booking_repo: Type[BookingRepo],
        property_repo: Type[BookingPropertyRepo],
        global_id_decoder: Callable,
        check_profitbase_property_service: CheckProfitbasePropertyService,
        activate_booking_class: ActivateBookingService,
        amocrm_class: type[amocrm.AmoCRM],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="ПОВТОРНАЯ АКТИВАЦИЯ БРОНИ | AMOCRM, PORTAL, PROFITBASE"
        )
        self.property_repo: BookingPropertyRepo = property_repo()
        self.check_profitbase_property_service: CheckProfitbasePropertyService = check_profitbase_property_service

        self.check_booking_task: Any = check_booking_task
        self.create_booking_log_task: Any = create_booking_log_task
        self.global_id_decoder: Callable = global_id_decoder

        self.period_days: int = booking_config["period_days"]
        self.booking_time_minutes: int = booking_config["time_minutes"]
        self.booking_time_seconds: int = booking_config["time_seconds"]
        self.activate_booking: ActivateBookingService = activate_booking_class
        self.amocrm_class: type[amocrm.AmoCRM] = amocrm_class

        self.connection_options: dict[str, Any] = dict(
            user=backend_config["db_user"],
            host=backend_config["db_host"],
            port=backend_config["db_port"],
            database=backend_config["db_name"],
            password=backend_config["db_password"],
        )
        self.logger: structlog.BoundLogger = structlog.get_logger(__name__)

    async def __call__(
            self,
            user_id: int,
            booking_id: int,
    ) -> Booking:
        filters: dict[str, Any] = dict(id=booking_id)
        if not await self.booking_repo.exists(filters=filters):
            raise BookingNotFoundError

        booking: Booking = await self.booking_repo.retrieve(
            filters=filters, related_fields=["user", "project", "property", "building"]
        )
        if await booking.property.bookings.filter(active=True).count() > 0:
            raise BookingUnfinishedExistsError

        if booking.property.status in (
                booking.property.statuses.SOLD,
                booking.property.statuses.BOOKED
        ):
            raise BookingPropertyMissingError

        if any(getattr(booking.property, arg) for arg in FORBIDDEN_FOR_BOOKING_PROPERTY_PARAMS):
            raise BookingForbiddenError

        property_status, property_available = await self.check_profitbase_property_service(
            booking.property
        )
        property_status_bool = property_status == booking.property.statuses.FREE
        if not property_available or not property_status_bool:
            if not await self.check_property_in_amo(booking):
                property_data: dict[str, Any] = dict(status=property_status)
                await self.property_repo.update(booking.property, data=property_data)
                self.logger.info(
                    f"Объект недвижимости недоступен. booked={property_status_bool}, in_deal={property_available}"
                )
                raise BookingPropertyAlreadyBookedError

        property_data: dict[str, Any] = dict(status=booking.property.statuses.BOOKED)

        data: dict[str, datetime] = dict(
            expires=datetime.datetime.now(tz=UTC) + datetime.timedelta(minutes=self.booking_time_minutes)
        )
        await self.booking_update(booking, data=data)

        await self.activate_booking(booking=booking,
                                    amocrm_substage=BookingSubstages.START)

        await self.property_repo.update(booking.property, data=property_data)

        filters: dict[str, Any] = dict(active=True, id=booking.id, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["project__city", "property", "floor", "building", "ddu", "agent", "agency"],
            prefetch_fields=["ddu__participants"],
        )
        taskchain_slugs: list[str] = [
            OnlineBookingSlug.ACCEPT_OFFER.value,
            FastBookingSlug.ACCEPT_OFFER.value,
            FreeBookingSlug.ACCEPT_OFFER.value,
        ]
        booking.tasks = await get_booking_tasks(
            booking_id=booking.id, task_chain_slug=taskchain_slugs
        )
        return booking

    async def check_property_in_amo(self, booking: Booking) -> bool:
        """
        Если квартира находится в статусе бронь - то проверяем в какой сделке она сейчас находится.
        Если сделка, в которой находится квартира, совпадает с текущей - то мы продлеваем быструю бронь.
        """
        lead: AmoLead = await self._get_amo_lead(lead_id=booking.amocrm_id)

        amocrm_enum: int | None = None
        building_name: str | None = None
        property_number: str | None = None
        for field in lead.custom_fields_values:
            match field.field_id:
                case self.amocrm_class.project_field_id:
                    # Объект
                    amocrm_enum: int = field.values[0].enum_id
                case self.amocrm_class.house_field_id:
                    # Дом
                    building_name: str = field.values[0].value
                case self.amocrm_class.room_number_field_id:
                    # Номер помещения
                    property_number: str = field.values[0].value

        if not all((amocrm_enum, building_name, property_number)):
            return False

        if await self._check_property_in_cabinet_db(
            booking=booking,
            amocrm_enum=amocrm_enum,
            building_name=building_name,
            property_number=property_number,
        ):
            # Если квартира находится в сделке, которая совпадает с текущей, то продлеваем бронь.
            return True
        return False

    async def _get_amo_lead(self, lead_id: int) -> AmoLead:
        async with await self.amocrm_class() as amo:
            lead: AmoLead = await amo.fetch_lead(lead_id=lead_id)
        if not lead:
            raise AmoFetchLeadNotFoundError
        return lead

    async def _check_property_in_cabinet_db(
        self,
        booking: Booking,
        amocrm_enum: int,
        building_name: str,
        property_number: str,
    ) -> bool:
        """
        Проверяем, что квартира, которую мы хотим забронировать, совпадает с квартирой, которая находится в сделке.
        """
        property_: Property = await self.property_repo.retrieve(
            filters=dict(
                project__amocrm_enum=amocrm_enum,
                number=property_number,
                section__building__name=building_name,
            ),
        )
        print(f'{property_=}')
        print(f"{booking.property=}")
        print(f'{property_.id != booking.property.id=}')
        if property_.id != booking.property.id:
            return False
        return True


class BookingRepeatV2(BaseBookingCase, BookingLogMixin):
    def __init__(
        self,
        check_booking_task: Any,
        create_booking_log_task: Any,
        booking_config: dict[str, Any],
        backend_config: dict[str, Any],
        booking_repo: Type[BookingRepo],
        property_repo: Type[BookingPropertyRepo],
        global_id_decoder: Callable,
        check_profitbase_property_service: CheckProfitbasePropertyService,
        activate_booking_class: ActivateBookingService,
        amocrm_class: type[amocrm.AmoCRM],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="ПОВТОРНАЯ АКТИВАЦИЯ БРОНИ | AMOCRM, PORTAL, PROFITBASE"
        )
        self.property_repo: BookingPropertyRepo = property_repo()
        self.check_profitbase_property_service: CheckProfitbasePropertyService = check_profitbase_property_service

        self.check_booking_task: Any = check_booking_task
        self.create_booking_log_task: Any = create_booking_log_task
        self.global_id_decoder: Callable = global_id_decoder

        self.period_days: int = booking_config["period_days"]
        self.booking_time_minutes: int = booking_config["time_minutes"]
        self.booking_time_seconds: int = booking_config["time_seconds"]
        self.activate_booking: ActivateBookingService = activate_booking_class
        self.amocrm_class: type[amocrm.AmoCRM] = amocrm_class

        self.connection_options: dict[str, Any] = dict(
            user=backend_config["db_user"],
            host=backend_config["db_host"],
            port=backend_config["db_port"],
            database=backend_config["db_name"],
            password=backend_config["db_password"],
        )
        self.logger = structlog.get_logger("booking_repeat")

    async def __call__(
        self,
        user_id: int,
        booking_id: int,
    ) -> Booking:
        filters: dict[str, Any] = dict(id=booking_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters, related_fields=["user", "project", "property", "building"]
        )
        try:
            await self.validate_booking(booking=booking)
        except (
            BookingNotFoundError,
            BookingUnfinishedExistsError,
            BookingPropertyMissingError,
            BookingForbiddenError,
            BookingPropertyAlreadyBookedError,
            AmoFetchLeadNotFoundError,
        ) as exc:
            self.logger.info(f"Booking={booking} validation failed: {str(exc)}")
            raise exc

        property_data: dict[str, Any] = dict(status=booking.property.statuses.BOOKED)
        data: dict[str, datetime.datetime] = dict(
            expires=datetime.datetime.now(tz=UTC) + datetime.timedelta(minutes=self.booking_time_minutes)
        )
        await self.booking_update(booking, data=data)
        await self.activate_booking_service(booking=booking)
        await self.property_repo.update(booking.property, data=property_data)

        return await self.retrieve_updated_booking(booking_id=booking.id, user_id=user_id)

    async def validate_booking(self, booking: Booking) -> None:
        if not booking:
            raise BookingNotFoundError

        if await booking.property.bookings.filter(active=True).count() > 0:
            raise BookingUnfinishedExistsError

        if booking.property.status in (
            booking.property.statuses.SOLD,
            booking.property.statuses.BOOKED
        ):
            raise BookingPropertyMissingError

        if any(getattr(booking.property, arg) for arg in FORBIDDEN_FOR_BOOKING_PROPERTY_PARAMS):
            raise BookingForbiddenError

        property_status, property_available = await self.check_profitbase_property_service(booking.property)
        property_status_bool = property_status == booking.property.statuses.FREE
        if not property_available or not property_status_bool:
            if not await self.check_property_in_amo(booking):
                property_data: dict[str, Any] = dict(status=property_status)
                await self.property_repo.update(booking.property, data=property_data)
                self.logger.info(
                    f"Объект недвижимости недоступен. booked={property_status_bool}, in_deal={property_available}"
                )
                raise BookingPropertyAlreadyBookedError

    async def activate_booking_service(self, booking: Booking) -> None:
        await self.activate_booking(booking=booking, amocrm_substage=BookingSubstages.START)

    async def retrieve_updated_booking(self, booking_id: int, user_id: int) -> Booking:
        filters: dict[str, Any] = dict(active=True, id=booking_id, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["project__city", "property", "floor", "building", "ddu", "agent", "agency"],
            prefetch_fields=["ddu__participants"],
        )
        return booking

    async def check_property_in_amo(self, booking: Booking) -> bool:
        """
        Если квартира находится в статусе бронь - то проверяем в какой сделке она сейчас находится.
        Если сделка, в которой находится квартира, совпадает с текущей - то мы продлеваем быструю бронь.
        """
        lead: AmoLead = await self._get_amo_lead(lead_id=booking.amocrm_id)

        amocrm_enum: int | None = None
        building_name: str | None = None
        property_number: str | None = None
        for field in lead.custom_fields_values:
            match field.field_id:
                case self.amocrm_class.project_field_id:
                    # Объект
                    amocrm_enum: int = field.values[0].enum_id
                case self.amocrm_class.house_field_id:
                    # Дом
                    building_name: str = field.values[0].value
                case self.amocrm_class.room_number_field_id:
                    # Номер помещения
                    property_number: str = field.values[0].value

        if not all((amocrm_enum, building_name, property_number)):
            return False

        if await self._check_property_in_cabinet_db(
            booking=booking,
            amocrm_enum=amocrm_enum,
            building_name=building_name,
            property_number=property_number,
        ):
            # Если квартира находится в сделке, которая совпадает с текущей, то продлеваем бронь.
            return True
        return False

    async def _get_amo_lead(self, lead_id: int) -> AmoLead:
        async with await self.amocrm_class() as amo:
            lead: AmoLead = await amo.fetch_lead(lead_id=lead_id)
        if not lead:
            raise AmoFetchLeadNotFoundError
        return lead

    async def _check_property_in_cabinet_db(
        self,
        booking: Booking,
        amocrm_enum: int,
        building_name: str,
        property_number: str,
    ) -> bool:
        """
        Проверяем, что квартира, которую мы хотим забронировать, совпадает с квартирой, которая находится в сделке.
        """
        property_: Property = await self.property_repo.retrieve(
            filters=dict(
                project__amocrm_enum=amocrm_enum,
                number=property_number,
                section__building__name=building_name,
            ),
        )
        if property_.id != booking.property.id:
            return False
        return True
