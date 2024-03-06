from pydantic import Field

from ..entities import BaseBookingCamelCaseModel


class RequestCreateBookingModel(BaseBookingCamelCaseModel):
    """
    Модель запроса создания сделки
    """
    property_global_id: str
    payment_method_slug: str | None = Field(default=None)
    mortgage_type_by_dev: bool | None = Field(default=None, alias="mortgageType")
    mortgage_program_name: str | None = Field(default=None)
    calculator_options: str | None = Field(default=None)
    property_slug: str
    booking_type_id: int
