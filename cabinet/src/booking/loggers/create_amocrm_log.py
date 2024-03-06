from typing import Any, Type

from common.unleash.client import UnleashClient
from config.feature_flags import FeatureFlags
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
            if self.__is_strana_lk_2882_enable:
                await amocrm.create_note_v4(**note_data)
            else:
                await amocrm.create_note(**note_data)

    @property
    def __is_strana_lk_2882_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_2882)
