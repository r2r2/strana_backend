from pydantic import Field

from src.mortgage.entities import BaseMortgageSchema


class _ValuesSchema(BaseMortgageSchema):
    """
    Схема параметров расчета
    """
    city: str = Field(..., description="Город")
    property_type: str = Field(..., description="Тип объекта", alias="propertyTypes")
    property_cost: int = Field(..., description="Стоимость объекта", alias="cost")
    initial_fee: int = Field(..., description="Первоначальный взнос", alias="initialPayment")
    credit_term: int = Field(..., description="Срок кредита, лет", alias="loanPeriod")
    mortgage_programs: list[str] | None = Field(description="Ипотечные программы(слаги)", alias="mortgageTypes")
    banks: list[str] | None = Field(description="Банки(UIDs)")
    income_confirmation: str | None = Field(description="Подтверждение дохода", alias="proofOfIncomeTypes")


class SelectedOfferSchema(BaseMortgageSchema):
    """
    Схема выбранных предложений
    """
    program: str = Field(..., description="Выбранная программа(слаг)", alias="mortgageType")
    bank: str = Field(..., description="Выбранный банк", alias='bankId')
    monthly_payment: int = Field(..., description="Ежемесячный платеж", alias="monthlyPaymentAmount")
    percent_rate: float = Field(..., description="Процентная ставка", alias="rate")
    credit_term: int = Field(..., description="Срок кредита, лет", alias="maxCreditPeriod")
    external_code: str | None = Field(description="Внешний код", alias="externalCode")
    name: str = Field(..., description="Название предложения")
    uid: str | None = Field(description="Для синхронизации с ДВИЖ", alias="bankUuid")
    bank_name: str | None = Field(description="Название банка", alias="bankName")


class _ClientSchema(BaseMortgageSchema):
    """
    Схема клиента
    """
    name: str = Field(..., description="Имя")
    surname: str = Field(..., description="Фамилия")
    patronymic: str | None = Field(description="Отчество")
    phone: str = Field(..., description="Телефон")


class CreateMortgageTicketSchema(BaseMortgageSchema):
    """
    Схема создания заявки на ипотеку
    """
    booking_id: int = Field(..., description="ID брони", alias="bookingId")
    values: _ValuesSchema = Field(..., description="Параметры расчета")
    offers: list[SelectedOfferSchema] = Field(..., description="Выбранные предложения")
    client: _ClientSchema = Field(..., description="Персональные данные")
