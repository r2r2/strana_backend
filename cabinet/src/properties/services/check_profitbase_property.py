# pylint: disable=arguments-differ

from typing import Any, Callable, Optional, Type

from src.booking.decorators import logged_action
from src.booking.entities import BaseBookingService
from src.booking.mixins import BookingLogMixin
from src.booking.types import BookingProfitBase
from src.properties.repos import Property


class CheckProfitbasePropertyService(BaseBookingService, BookingLogMixin):
    def __init__(
        self,
        global_id_decoder: Callable,
        profitbase_class: Type[BookingProfitBase],
    ):
        self.global_id_decoder = global_id_decoder
        self.profitbase_class = profitbase_class

    # @logged_action(content="ПРОВЕРКА | PROFITBASE")
    async def __call__(self, booking_property: Property) -> tuple[int, bool]:
        _, property_id = self.global_id_decoder(global_id=booking_property.global_id)
        async with await self.profitbase_class() as profitbase:
            if profitbase.errors:
                key_ok: bool = False
                mapped_status: int = booking_property.statuses.FREE
            else:
                property_data: Optional[dict[str, Any]] = await profitbase.get_property(
                    property_id=property_id
                )
                if not property_data:
                    key_ok: bool = True
                    mapped_status: int = booking_property.statuses.FREE
                else:
                    key_ok: bool = property_data["status"] == profitbase.status_success
                    mapped_status: int = getattr(
                        booking_property.statuses,
                        profitbase.status_mapping.get(property_data["status"], "BOOKED"),
                    )
        return mapped_status, key_ok
