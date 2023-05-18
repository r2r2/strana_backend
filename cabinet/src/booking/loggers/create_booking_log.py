from copy import copy
from typing import Any, Optional, Type, Union

from ..repos import BookingLogRepo
from ..entities import BaseBookingService
from ..types import BookingORM


class CreateBookingLogLogger(BaseBookingService):
    """
    Создание лога бронирования
    """
    def __init__(
        self,
        booking_log_repo: Type[BookingLogRepo],
        orm_class: Optional[Type[BookingORM]] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.booking_log_repo: BookingLogRepo = booking_log_repo()

        self.orm_class: Union[Type[BookingORM], None] = orm_class
        self.orm_config: Union[dict[str, Any], None] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self, log_data: dict[str, Any]) -> None:
        await self.booking_log_repo.create(data=log_data)
