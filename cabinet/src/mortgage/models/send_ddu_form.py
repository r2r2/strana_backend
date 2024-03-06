from pydantic import Field

from src.mortgage.entities import BaseMortgageSchema


class _ClientSchema(BaseMortgageSchema):
    """
    Форма ПНД
    """
    name: str = Field(..., description="Имя")
    surname: str = Field(..., description="Фамилия")
    patronymic: str | None = Field(description="Отчество")
    phone: str = Field(..., description="Телефон")
    email: str | None = Field(description="Email")


class SendDDUFormSchema(BaseMortgageSchema):
    booking_id: int = Field(..., description="ID брони", alias="bookingId")
    client: _ClientSchema | None = Field(description="Персональные данные")
