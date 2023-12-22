from datetime import datetime
from typing import Optional
from pydantic import Field

from common.pydantic import CamelCaseBaseModel


class RequestBindBookingPropertyModel(CamelCaseBaseModel):
    property_id: int
    property_type_slug: str = Field(default=None)
    booking_id: int
    booking_type_id: int


class ResponseBindBookingPropertyModel(CamelCaseBaseModel):
    id: int
    active: bool
    property_id: int
    expires: Optional[datetime]
    created: datetime


class RequestUnbindBookingPropertyModel(CamelCaseBaseModel):
    booking_id: int
