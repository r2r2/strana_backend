from datetime import datetime
from typing import Optional
from pydantic import Field

from common.pydantic import CamelCaseBaseModel


class RequestBindBookingPropertyModel(CamelCaseBaseModel):
    property_id: int
    payment_method_slug: str | None = Field(default=None)
    mortgage_type_by_dev: bool | None = Field(default=None, alias="mortgageType")
    mortgage_program_name: str | None = Field(default=None)
    calculator_options: str | None = Field(default=None)
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
