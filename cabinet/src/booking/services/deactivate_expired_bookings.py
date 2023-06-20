from copy import copy
from datetime import datetime
from typing import Any, Optional, Type

from pytz import UTC
from tortoise import Tortoise

from common.amocrm import AmoCRM
from common.profitbase import ProfitBase
from common.requests import GraphQLRequest
from src.booking.loggers.wrappers import booking_changes_logger
from src.properties.repos import PropertyRepo
from ..constants import BookingStages, BookingSubstages
from ..entities import BaseBookingService
from ..repos import Booking, BookingRepo


class DeactivateExpiredBookingsService(BaseBookingService):
    """
    Деактивация бронирований, которые должны были деактивироваться по таймеру.

    По какой-то причине тестовые квартиры не деактивировались по таймеру.
    Вероятнее всего это связано с тем, что Redis терял таску при проливке пайплайна.
    """

    query_type: str = "changePropertyStatus"
    query_name: str = "changePropertyStatus.graphql"
    query_directory: str = "/src/booking/queries/"

    def __init__(
        self,
        backend_config: dict[str, str],
        booking_repo: Type[BookingRepo],
        amocrm_class: Type[AmoCRM],
        request_class: Type[GraphQLRequest],
        profitbase_class: Type[ProfitBase],
        property_repo: Type[PropertyRepo],
        orm_class: Optional[Type[Tortoise]] = None,
        orm_config: Optional[dict[str, Any]] = None,
        create_booking_log_task: Optional[Any] = None,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.property_repo: PropertyRepo = property_repo()

        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.request_class: Type[GraphQLRequest] = request_class
        self.profitbase_class: Type[ProfitBase] = profitbase_class
        self.create_booking_log_task: Any = create_booking_log_task

        self.login: str = backend_config["internal_login"]
        self.password: str = backend_config["internal_password"]
        self.backend_url: str = backend_config["url"] + backend_config["graphql"]

        self.orm_class: Optional[Type[Tortoise]] = orm_class
        self.orm_config: Optional[dict[str, Any]] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)
        self.booking_update = booking_changes_logger(self.booking_repo.update, self, content="Деактивация бронирований")

    async def __call__(self) -> None:
        # Не должно быть активных оплаченных бронирований,
        # которые должны быть деактивированы по таймеру
        filters = dict(active=True, price_payed=True, should_be_deactivated_by_timer=True)
        confused_bookings: list[Booking] = await self.booking_repo.list(filters=filters)
        for booking in confused_bookings:
            booking_data = dict(should_be_deactivated_by_timer=False)
            await self.booking_update(booking=booking, data=booking_data)

        # Деактивация бронирований, которые просрочены по таймеру и не оплачены
        filters: dict[str, Any] = dict(
            active=True,
            price_payed=False,
            expires__lte=datetime.now(tz=UTC),
            should_be_deactivated_by_timer=True,
        )
        expired_bookings: list[Booking] = await self.booking_repo.list(
            filters=filters, related_fields=["user", "project", "project__city", "property", "building"]
        )
        for booking in expired_bookings:
            booking_data: dict[str, Any] = dict(
                active=False,
                profitbase_booked=False,
                amocrm_stage=BookingStages.START,
                amocrm_substage=BookingSubstages.START,
                should_be_deactivated_by_timer=False,
            )
            if booking.property:
                property_data: dict[str, Any] = dict(status=booking.property.statuses.FREE)
                await self.property_repo.update(booking.property, data=property_data)
            if booking.step_one() and not booking.step_two() and booking.amocrm_id:
                await self._amocrm_unbooking(booking)
            elif booking.step_two():
                await self._profitbase_unbooking(booking)
                await self._amocrm_unbooking(booking)
            await self.booking_update(booking=booking, data=booking_data)
            if booking.property:
                await self._backend_unbooking(booking)

    async def _amocrm_unbooking(self, booking: Booking) -> int:
        """
        Разбронирование amocrm
        """
        async with await self.amocrm_class() as amocrm:
            lead_options: dict[str, Any] = dict(
                status=BookingSubstages.START,
                lead_id=booking.amocrm_id,
                city_slug=booking.project.city.slug,
            )
            data: list[Any] = await amocrm.update_lead(**lead_options)
            lead_id: int = data[0]["id"]
        return lead_id

    async def _profitbase_unbooking(self, booking: Booking) -> bool:
        """
        Разбронирование profitbase
        """
        async with await self.profitbase_class() as profitbase:
            data: dict[str, bool] = await profitbase.unbook_property(deal_id=booking.amocrm_id)
        success: bool = data["success"]
        return success

    async def _backend_unbooking(self, booking: Booking) -> bool:
        """
        Разбрование портал
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
