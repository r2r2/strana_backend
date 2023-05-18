from typing import Any, Type

from ..entities import BaseBookingService
from ..types import BookingAmoCRM


class CreateAmoCRMLogLogger(BaseBookingService):
    """
    Создание лога АМО
    """

    def __init__(self, amocrm_class: Type[BookingAmoCRM]) -> None:
        self.amocrm_class: Type[BookingAmoCRM] = amocrm_class

    async def __call__(self, note_data: dict[str, Any]) -> None:
        async with await self.amocrm_class() as amocrm:
            await amocrm.create_note(**note_data)
