from pydantic import Field

from src.mortgage_calculator.entities import BaseMortgageSchema


class _ParametersSchema(BaseMortgageSchema):
    """
    Схема параметров расчета
    """
    city: str = Field(..., description="Город")
    property_type: str = Field(..., description="Тип объекта")
    property_cost: int = Field(..., description="Стоимость объекта")
    initial_fee: int = Field(..., description="Первоначальный взнос")
    credit_term: int = Field(..., description="Срок кредита, лет")
    mortgage_programs: list[str] = Field(..., description="Ипотечные программы(слаги)")
    banks: list[str] = Field(..., description="Банки(UIDs)")
    income_confirmation: str = Field(..., description="Подтверждение дохода")


class _SelectedOfferSchema(BaseMortgageSchema):
    """
    Схема выбранных предложений
    """
    program: str = Field(..., description="Выбранная программа(слаг)")
    bank: str = Field(..., description="Выбранный банк(UID)")
    monthly_payment: int = Field(..., description="Ежемесячный платеж")
    procent_rate: float = Field(..., description="Процентная ставка")
    credit_term: int = Field(..., description="Срок кредита, лет")


class _ClientSchema(BaseMortgageSchema):
    """
    Схема клиента
    """
    first_name: str = Field(..., description="Имя")
    last_name: str = Field(..., description="Фамилия")
    patronymic: str | None = Field(description="Отчество")
    phone: str = Field(..., description="Телефон")


class CreateMortgageTicketSchema(BaseMortgageSchema):
    """
    Схема создания заявки на ипотеку
    """
    booking_id: int = Field(..., description="ID брони")
    parameters: _ParametersSchema = Field(..., description="Параметры расчета")
    selected_offers: list[_SelectedOfferSchema] = Field(..., description="Выбранные предложения")
    client: _ClientSchema = Field(..., description="Клиент")






