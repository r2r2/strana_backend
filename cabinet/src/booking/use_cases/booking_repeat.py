import datetime
from typing import Any, Callable, Type

from pytz import UTC

from src.properties.services import CheckProfitbasePropertyService
from ..constants import (FORBIDDEN_FOR_BOOKING_PROPERTY_PARAMS,
                         BookingSubstages)
from ..entities import BaseBookingCase
from ..exceptions import (BookingForbiddenError, BookingPropertyMissingError,
                          BookingPropertyUnavailableError,
                          BookingNotFoundError, BookingUnfinishedExistsError)
from ..loggers import booking_changes_logger
from ..mixins import BookingLogMixin
from ..repos import Booking, BookingRepo
from ..services import ActivateBookingService
from ..types import (BookingPropertyRepo, BookingSqlUpdateRequest)


class BookingRepeat(BaseBookingCase, BookingLogMixin):
    def __init__(
            self,
            check_booking_task: Any,
            create_booking_log_task: Any,
            booking_config: dict[str, Any],
            backend_config: dict[str, Any],
            booking_repo: Type[BookingRepo],
            property_repo: Type[BookingPropertyRepo],
            request_class: Type[BookingSqlUpdateRequest],
            global_id_decoder: Callable,
            check_profitbase_property_service: CheckProfitbasePropertyService,
            activate_booking_class: ActivateBookingService,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_update = booking_changes_logger(
            self.booking_repo.update, self, content="ПОВТОРНАЯ АКТИВАЦИЯ БРОНИ | AMOCRM, PORTAL, PROFITBASE"
        )
        self.property_repo: BookingPropertyRepo = property_repo()
        self.check_profitbase_property_service: CheckProfitbasePropertyService = check_profitbase_property_service

        self.check_booking_task: Any = check_booking_task
        self.create_booking_log_task: Any = create_booking_log_task
        self.request_class: Type[BookingSqlUpdateRequest] = request_class
        self.global_id_decoder: Callable = global_id_decoder

        self.period_days: int = booking_config["period_days"]
        self.booking_time_minutes: int = booking_config["time_minutes"]
        self.booking_time_seconds: int = booking_config["time_seconds"]
        self.activate_booking: ActivateBookingService = activate_booking_class

        self.connection_options: dict[str, Any] = dict(
            user=backend_config["db_user"],
            host=backend_config["db_host"],
            port=backend_config["db_port"],
            database=backend_config["db_name"],
            password=backend_config["db_password"],
        )

    async def __call__(
            self,
            user_id: int,
            booking_id: int,
    ) -> Booking:
        print("***BookingRepeat***")
        filters: dict[str, Any] = dict(id=booking_id)
        if not await self.booking_repo.exists(filters=filters):
            raise BookingNotFoundError

        booking: Booking = await self.booking_repo.retrieve(
            filters=filters, related_fields=["user", "project", "property", "building"]
        )
        print(f"{booking=}")
        print(f'{booking.active=}')
        print(f"{booking.property=}")
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
            booking.property)
        print(f"{property_status=}")
        print(f"{property_available=}")
        property_status_bool = property_status == booking.property.statuses.FREE
        print(f"{property_status_bool=}")
        print(f"{property_status=}")
        if not property_available or not property_status_bool:
            print("if not property_available or not property_status_bool:")
            property_data: dict[str, Any] = dict(status=property_status)
            await self.property_repo.update(booking.property, data=property_data)
            raise BookingPropertyUnavailableError(property_status_bool, property_available)

        property_data: dict[str, Any] = dict(status=booking.property.statuses.BOOKED)

        data: dict[str] = dict(
            expires=datetime.datetime.now(tz=UTC) + datetime.timedelta(minutes=self.booking_time_minutes)
        )
        await self.booking_update(booking, data=data)

        await self.activate_booking(booking=booking,
                                    amocrm_substage=BookingSubstages.START)

        await self.property_repo.update(booking.property, data=property_data)

        filters: dict[str, Any] = dict(active=True, id=booking.id, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["project", "project__city", "property", "floor", "building", "ddu", "agent", "agency"],
            prefetch_fields=["ddu__participants"],
        )
        print(f"BookingRepeat done: {booking=}")
        return booking
