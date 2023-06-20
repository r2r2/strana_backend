# pylint: disable=too-many-statements

import base64
from datetime import datetime, timedelta
from typing import Any, Callable, NamedTuple, Optional, Type, Union

import sentry_sdk
from pytz import UTC
from src.buildings.repos.building import Building, BuildingBookingType
from src.properties.repos import Property
from src.properties.services import CheckProfitbasePropertyService

from ...properties.constants import PropertyStatuses
from ..constants import (FORBIDDEN_FOR_BOOKING_PROPERTY_PARAMS,
                         BookingCreatedSources, BookingStages,
                         BookingSubstages)
from ..loggers.wrappers import booking_changes_logger
from ..entities import BaseBookingCase
from ..exceptions import (BookingForbiddenError, BookingPropertyMissingError,
                          BookingPropertyUnavailableError,
                          BookingUnfinishedExistsError)
from ..mixins import BookingLogMixin
from ..models import RequestAcceptContractModel
from ..repos import Booking, BookingRepo
from ..types import (BookingPropertyRepo, BookingQuerySet,
                     BookingSqlUpdateRequest)


class BookingTypeNamedTuple(NamedTuple):
    price: int
    period: int


class AcceptContractCase(BaseBookingCase, BookingLogMixin):
    """
    Принятие оферты
    """

    # NOTE: Технический долг. Проверку делать по запросу к бэку, а не смотреть тип бронирования в бд
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
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.property_repo: BookingPropertyRepo = property_repo()
        self.check_profitbase_property_service: CheckProfitbasePropertyService = check_profitbase_property_service

        self.check_booking_task: Any = check_booking_task
        self.create_booking_log_task: Any = create_booking_log_task
        self.request_class: Type[BookingSqlUpdateRequest] = request_class
        self.global_id_decoder: Callable = global_id_decoder

        self.period_days: int = booking_config["period_days"]
        self.booking_time_minutes: int = booking_config["time_minutes"]
        self.booking_time_seconds: int = booking_config["time_seconds"]

        self.connection_options: dict[str, Any] = dict(
            user=backend_config["db_user"],
            host=backend_config["db_host"],
            port=backend_config["db_port"],
            database=backend_config["db_name"],
            password=backend_config["db_password"],
        )
        self.booking_create = booking_changes_logger(self.booking_repo.create, self, content="Создание брони")
        self.booking_update = booking_changes_logger(self.booking_repo.update, self, content="Обновление брони")
        self.booking_delete = booking_changes_logger(self.booking_repo.delete, self, content="Удаление брони")

    async def __call__(
        self,
        user_id: int,
        origin: Union[str, None],
        payload: RequestAcceptContractModel,
    ) -> Booking:

        filters: dict[str, Any] = dict(
            active=True,
            user_id=user_id,
            price_payed=False,
            expires__gte=(datetime.now(tz=UTC)),
            contract_accepted=True,
        )
        if await self.booking_repo.exists(filters=filters):
            raise BookingUnfinishedExistsError

        if booking_id := payload.booking_id:
            booking_data: dict = payload.dict(exclude={"booking_id", "property_id", "booking_type_id"})
            booking: Booking = await self.booking_repo.retrieve(filters=dict(id=booking_id))
            booking: Booking = await self.booking_update(booking=booking, data=booking_data)
            filters: dict[str, Any] = dict(active=True, id=booking.id, user_id=user_id)
            booking: Booking = await self.booking_repo.retrieve(
                filters=filters,
                related_fields=["project", "project__city", "property", "floor", "building", "ddu", "agent", "agency"],
                prefetch_fields=["ddu__participants"],
            )
            return booking

        data: dict[str, Any] = payload.dict()
        data.update({
            "should_be_deactivated_by_timer": True,
            "user_id": user_id,
        })

        filters: dict[str, Any] = dict(property_id=data["property_id"], active=True)
        bookings_qs: BookingQuerySet[Booking] = self.booking_repo.list(filters=filters)
        property_filters: dict[str, Any] = dict(id=data["property_id"])
        booking_property: Property = await self.property_repo.retrieve(
            filters=property_filters,
            related_fields=["building", "project"],
            prefetch_fields=[
                dict(relation="bookings", queryset=bookings_qs),
                "building__booking_types",
            ],
        )

        if not booking_property:
            sentry_sdk.capture_message(
                "cabinet/AcceptContractCase: BookingPropertyMissingError: Квартира не найдена"
            )
            raise BookingPropertyMissingError

        building: Optional[Building] = booking_property.building

        profitbase_id = base64.b64decode(booking_property.global_id).decode("utf-8").split(":")[-1]
        property_data = {
            "status": PropertyStatuses.to_label(str(booking_property.status)),
            "profitbase_id": profitbase_id,
            "number": booking_property.number,
            "preferential_mortgage": booking_property.preferential_mortgage,
            "maternal_capital": booking_property.maternal_capital,
        }
        if building:
            property_data["building_name"] = building.name
        if booking_property.project:
            property_data["project_name"] = booking_property.project.name

        if await booking_property.bookings.filter(active=True).count() > 0:
            sentry_sdk.set_context(
                "bookings",
                {
                    "bookings": [
                        {
                            "active": booking.active,
                            "amocrm_id": booking.amocrm_id,
                            "contract_accepted": booking.contract_accepted,
                            "personal_filled": booking.personal_filled,
                            "params_checked": booking.params_checked,
                            "price_payed": booking.price_payed,
                        }
                        for booking in booking_property.bookings
                    ]
                },
            )
            sentry_sdk.capture_message(
                "cabinet/AcceptContractCase: BookingPropertyMissingError: "
                "У квартиры есть активные бронирования"
            )
            raise BookingPropertyMissingError

        if booking_property.status in (
                booking_property.statuses.SOLD,
                booking_property.statuses.BOOKED
        ):
            sentry_sdk.capture_message(
                "cabinet/AcceptContractCase: BookingPropertyMissingError: Неверный статус квартиры"
            )
            raise BookingPropertyMissingError

        if any(getattr(booking_property, arg) for arg in FORBIDDEN_FOR_BOOKING_PROPERTY_PARAMS):
            sentry_sdk.capture_message(
                "cabinet/AcceptContractCase: BookingForbiddenError: Квартиру нельзя забронировать"
            )
            raise BookingForbiddenError

        # Проверка на то, что указанный тип бронирования был найден
        booking_type_id: Optional[int]
        try:
            booking_type_id = payload.booking_type_id
        except ValueError:
            booking_type_id = None
        selected_booking_type: Optional[Union[BuildingBookingType, BookingTypeNamedTuple]] = None
        building: Optional[Building] = booking_property.building
        for booking_type in building.booking_types:
            if booking_type.id == booking_type_id:
                selected_booking_type = booking_type
                break

        if selected_booking_type is None:
            selected_booking_type = BookingTypeNamedTuple(
                price=building.booking_price, period=building.booking_period
            )

        extra_data: dict[str, Any] = dict(
            origin=origin,
            amocrm_stage=BookingStages.START,
            amocrm_substage=BookingSubstages.START,
            expires=datetime.now(tz=UTC) + timedelta(minutes=self.booking_time_minutes),
            created_source=BookingCreatedSources.LK
        )
        if booking_property.building_id:
            additional_data: dict[str, Any] = dict(
                floor_id=booking_property.floor_id,
                project_id=booking_property.project_id,
                building_id=booking_property.building_id,
                payment_amount=selected_booking_type.price,
                final_payment_amount=booking_property.price,
                start_commission=building.default_commission,
                commission=building.default_commission,
                booking_period=selected_booking_type.period,
                until=datetime.now(tz=UTC) + timedelta(days=selected_booking_type.period),
            )
            extra_data.update(additional_data)

        data.update(extra_data)

        booking: Booking = await self.booking_create(data=data)
        setattr(booking, "property", booking_property)
        property_status, property_available = await self.check_profitbase_property_service(booking.property)
        property_status_bool = property_status == booking_property.statuses.FREE
        if not property_available or not property_status_bool:
            property_data: dict[str, Any] = dict(status=property_status)
            await self.booking_delete(booking=booking)
            await self.property_repo.update(booking_property, data=property_data)
            raise BookingPropertyUnavailableError(property_status_bool, property_available)

        property_data: dict[str, Any] = dict(status=booking_property.statuses.BOOKED)
        await self._backend_booking(booking=booking)
        await self.property_repo.update(booking_property, data=property_data)

        self.check_booking_task.apply_async((booking.id,), countdown=self.booking_time_seconds)

        filters: dict[str, Any] = dict(active=True, id=booking.id, user_id=user_id)
        booking: Booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["project", "project__city", "property", "floor", "building", "ddu", "agent", "agency"],
            prefetch_fields=["ddu__participants"],
        )
        return booking

    async def _backend_booking(self, booking: Booking) -> str:
        """
        Бронирование в портале
        """
        _, property_id = self.global_id_decoder(global_id=booking.property.global_id)
        request_options: dict[str, Any] = dict(
            table="properties_property",
            filters=dict(id=property_id),
            data=dict(status=booking.property.statuses.BOOKED),
            connection_options=self.connection_options,
        )
        async with self.request_class(**request_options) as response:
            result: str = response
        return result
