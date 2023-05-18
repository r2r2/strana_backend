from datetime import datetime
from typing import Optional

from common.pydantic import CamelCaseBaseModel


class RequestBindBookingPropertyModel(CamelCaseBaseModel):
    property_id: int
    booking_id: int
    booking_type_id: int


class ResponseBindBookingPropertyModel(CamelCaseBaseModel):
    id: int
    active: bool
    property_id: int
    expires: Optional[datetime]
    created: datetime
