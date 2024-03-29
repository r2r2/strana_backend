from pytz import UTC
from typing import Callable, Any
from datetime import datetime, timedelta

from common.profitbase import ProfitBase
from common.sentry.utils import send_sentry_log
from src.properties.repos import Property
from src.booking.constants import BookingCreatedSources, BookingStages
from src.booking.exceptions import (
    BookingPropertyUnavailableError,
    InactiveBookingNotFoundError,
)
from src.booking.repos import Booking, BookingRepo
from src.booking.entities import BaseBookingCase
from src.booking.types import BookingAmoCRM
from src.task_management.constants import OnlineBookingSlug, FastBookingSlug
from src.task_management.utils import get_booking_tasks


class RebookingCase(BaseBookingCase):
    """
    Кейс повторного бронирования
    """

    CREATED_SOURCE: str = BookingCreatedSources.LK
    BOOKING_STAGE: str = BookingStages.BOOKING

    def __init__(
        self,
        booking_repo: type[BookingRepo],
        amocrm_class: type[BookingAmoCRM],
        profit_base_class: type[ProfitBase],
        get_booking_reserv_time,
        global_id_decoder,
        check_booking_task: Any,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.amocrm_class: type[BookingAmoCRM] = amocrm_class
        self.profit_base_class: type[ProfitBase] = profit_base_class
        self.get_booking_reserv_time: Callable = get_booking_reserv_time
        self.global_id_decoder: Callable = global_id_decoder
        self.check_booking_task: Any = check_booking_task

    async def __call__(self, booking_id: int, user_id: int) -> Booking:
        booking_filters: dict = dict(active=False, id=booking_id, user_id=user_id)
        booking: Booking | None = await self.booking_repo.retrieve(
            filters=booking_filters,
            related_fields=[
                "building",
                "project__city",
                "property__section",
                "property__property_type",
                "floor",
                "agent",
                "agency",
                "booking_source",
            ],
            prefetch_fields=[
                "ddu__participants",
                "amocrm_status__group_status",
            ],
        )
        if not booking:
            sentry_ctx: dict[str, Any] = dict(
                booking_id=booking_id,
                user_id=user_id,
                booking_filters=booking_filters,
                ex=InactiveBookingNotFoundError,
            )
            await send_sentry_log(
                tag="RebookingCase",
                message="Booking not found",
                context=sentry_ctx,
            )
            raise InactiveBookingNotFoundError
        booking_property: Property = booking.property
        booking_reserv_time: float = await self.get_booking_reserv_time(
            created_source=self.CREATED_SOURCE,
            booking_property=booking_property,
        )
        expires: datetime = datetime.now(tz=UTC) + timedelta(hours=booking_reserv_time)
        booking_data: dict = dict(
            active=True,
            amocrm_stage=self.BOOKING_STAGE,
            amocrm_substage=self.BOOKING_STAGE,
            expires=expires,
        )
        updated_booking: Booking = await self.booking_repo.update(
            model=booking, data=booking_data
        )
        profit_base_is_booked: bool = await self._profit_base_booking(
            booking=updated_booking,
            property_id=self.global_id_decoder(booking_property.global_id)[1],
        )
        if profit_base_is_booked:
            await self._update_amo_booking(
                booking=booking,
                portal_property_id=self.global_id_decoder(booking_property.global_id)[1],
            )
        self.check_booking_task.apply_async((booking.id,), eta=expires, queue="scheduled")
        interested_task_chains: list[str] = [
            OnlineBookingSlug.ACCEPT_OFFER.value,
            FastBookingSlug.ACCEPT_OFFER.value,
        ]
        booking.tasks = await get_booking_tasks(
            booking_id=booking.id, task_chain_slug=interested_task_chains
        )
        return booking

    async def _update_amo_booking(
        self, booking: Booking, portal_property_id: int
    ) -> None:
        lead_options: dict = dict(
            lead_id=booking.amocrm_id,
            status=self.BOOKING_STAGE,
            property_id=portal_property_id,
        )
        async with await self.amocrm_class() as amocrm:
            await amocrm.update_lead(**lead_options)

    async def _profit_base_booking(self, booking: Booking, property_id: int) -> bool:
        """
        todo вынести в отдельный сервис для CreateBookingCase и RebookingCase
        Бронирование в profitbase
        """
        async with await self.profit_base_class() as profit_base:
            data: dict[str, bool] = await profit_base.book_property(
                property_id=property_id, deal_id=booking.amocrm_id
            )
            booked: bool = data.get("success", False)
            in_deal: bool = data.get("code", None) == profit_base.dealed_code
        profit_base_booked: bool = booked or in_deal
        if not profit_base_booked:
            sentry_ctx: dict[str, Any] = dict(
                data=data,
                booked=booked,
                in_deal=in_deal,
                amocrm_id=booking.amocrm_id,
                property_id=property_id,
                ex=BookingPropertyUnavailableError,
            )
            await send_sentry_log(
                tag="RebookingCase",
                message="Ошибка бронирования в profitbase",
                context=sentry_ctx,
            )
            raise BookingPropertyUnavailableError(booked, in_deal)
        return profit_base_booked
