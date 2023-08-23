from typing import Any, Optional, Type

from ..entities import BaseBookingCase
from ..models import BookingListFilters
from ..repos import Booking, BookingRepo, BookingTag, BookingTagRepo


class BookingListCase(BaseBookingCase):
    """
    Список бронирований
    """

    def __init__(self, booking_repo: Type[BookingRepo], booking_tag_repo: Type[BookingTagRepo]) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.booking_tag_repo: BookingTagRepo = booking_tag_repo()

    async def __call__(
        self,
        user_id: int,
        statuses: list,
        init_filters: BookingListFilters,
        property_types_filter: list,
    ) -> dict[str, Any]:
        filters: dict[str, Any] = dict(
            active=True,
            user_id=user_id,
            property_id__isnull=False,
            property__property_type__is_active=True,
            building_id__isnull=False,
            project_id__isnull=False,
        )
        additional_filters: dict = self._get_additional_filters(
            statuses=statuses,
            init_filters=init_filters,
            property_types_filter=property_types_filter,
        )
        filters.update(additional_filters)
        related_fields = [
            "property",
            "property__section",
            "property__property_type",
            "floor",
            "building",
            "project",
            "ddu",
            "amocrm_status",
            "agent",
            "agency",
        ]
        bookings: list[Booking] = await self.booking_repo.list(
            filters=filters,
            related_fields=related_fields,
            prefetch_fields=["amocrm_status__group_status"],
        )
        for booking in bookings:
            booking.booking_tags = await self._get_booking_tags(booking)
        data: dict[str, Any] = dict(result=bookings, count=len(bookings))

        return data

    async def _get_booking_tags(self, booking: Booking) -> Optional[list[BookingTag]]:
        tag_filters: dict[str, Any] = dict(
            is_active=True,
            group_statuses=booking.amocrm_status.group_status if booking.amocrm_status else None,
        )
        return (await self.booking_tag_repo.list(filters=tag_filters, ordering='-priority')) or None

    def _get_additional_filters(
        self,
        statuses: list,
        init_filters: BookingListFilters,
        property_types_filter: list,
    ) -> dict:
        additional_filters: dict = dict()
        if statuses:
            additional_filters.update(amocrm_stage__in=statuses)
        if property_types_filter:
            additional_filters.update(property__property_type__slug__in=property_types_filter)
        if init_filters:
            additional_filters.update(init_filters.dict(exclude_none=True))
        return additional_filters
