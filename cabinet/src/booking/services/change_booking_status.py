from copy import copy
from typing import Any, Optional, Type

from tortoise import Tortoise

from ..loggers.wrappers import booking_changes_logger
from ..entities import BaseBookingService
from ..repos import Booking, BookingRepo


class ChangeBookingStatusService(BaseBookingService):
    """
    Сервис смены статуса бронирования.
    """
    def __init__(
        self,
        booking_repo: Type[BookingRepo],
        orm_class: Optional[Type[Tortoise]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()

        self.orm_class: Optional[Type[Tortoise]] = orm_class
        self.orm_config: Optional[dict[str, Any]] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)
        self.booking_update = booking_changes_logger(self.booking_repo.update, self, content="Деактивация бронирования")

    async def __call__(self, booking_id: int, status: str) -> None:
        booking: Booking = await self.booking_repo.retrieve(filters=dict(id=booking_id, price_payed=False))
        if booking:
            await self.booking_repo.update(model=booking, data=dict(amocrm_stage=status, amocrm_substage=status))
