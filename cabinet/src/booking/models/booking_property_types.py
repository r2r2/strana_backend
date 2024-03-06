from typing import Optional

from src.booking.entities import BaseBookingModel


class _BookingPropertyType(BaseBookingModel):
    slug: Optional[str]
    label: Optional[str]


class ResponseBookingPropertyTypes(BaseBookingModel):
    propertyTypes: list[_BookingPropertyType]
