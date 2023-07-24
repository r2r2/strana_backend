from typing import Any, Type

from ..entities import BaseBookingCase
from ..repos import Booking, BookingRepo
from ..models import BookingListFilters


class BookingListCase(BaseBookingCase):
    """
    Список бронирований
    """

    def __init__(self, booking_repo: Type[BookingRepo]) -> None:
        self.booking_repo: BookingRepo = booking_repo()

    async def __call__(self, user_id: int, statuses: list, init_filters: BookingListFilters) -> dict[str, Any]:
        filters: dict[str, Any] = dict(
            active=True,
            user_id=user_id,
            property_id__isnull=False,
            building_id__isnull=False,
            project_id__isnull=False,
        )

        additional_filters: dict = self._get_additional_filters(statuses=statuses, init_filters=init_filters)
        filters.update(additional_filters)
        bookings: list[Booking] = await self.booking_repo.list(
            filters=filters,
            related_fields=["property", "floor", "building", "project", "ddu", "amocrm_status", "agent", "agency__city"]
        )
        data: dict[str, Any] = dict(result=bookings, count=len(bookings))
        return data

    def _get_additional_filters(self, statuses: list, init_filters: BookingListFilters) -> dict:
        additional_filters: dict = dict()
        if statuses:
            additional_filters.update(amocrm_stage__in=statuses)
        if init_filters:
            additional_filters.update(init_filters.dict(exclude_none=True))
        return additional_filters
