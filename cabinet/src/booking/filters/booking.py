from typing import Optional, Type
from pydantic import Field
from common import wrappers

from ..entities import BaseBookingFilter
from ..repos import BookingRepo


@wrappers.filterize
class BookingFilter(BaseBookingFilter):
    """
    Фильтр бронирований
    """

    property_id: Optional[int] = Field(alias="property", description="Фильтр по объекту")

    class Filter:
        repo: Type[BookingRepo] = BookingRepo
