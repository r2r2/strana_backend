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
    position: str | None = Field(description="Должность")
    company: str | None = Field(description="Компания")
    experience: str | None = Field(description="Стаж работы")
    average_salary: str | None = Field(description="Средняя зарплата", alias="averageSalary")


class _DocumentsSchema(BaseMortgageSchema):
    """
    Схема документов
    """
    passport: list[str | None] = Field(description="Все страницы паспорта", default_factory=list)
    snils: list[str | None] = Field(description="СНИЛС", default_factory=list)
    marriage_certificate: list[str | None] = Field(description="Свидетельство о браке", default_factory=list)
    child_birth_certificate: list[str | None] = Field(description="Свидетельство о рождении ребенка", default_factory=list)
    ndfl_2: list[str | None] = Field(description="Заполненная справка о доходах 2-НДФЛ", default_factory=list)
    labor_book: list[str | None] = Field(description="Трудовая книжка, заверенная работодателем", default_factory=list)


class _CoBorrowers(BaseMortgageSchema):
    """
    Схема созаемщиков
    """
    co_borrowers: str | None = Field(description="Созаемщики", alias="coBorrowers")

    # todo: move to independent schema for sending to calculator
    documents: list[str | None] | None = Field(description="Документы созаемщиков", default_factory=list)


class SendAmoDataSchema(BaseMortgageSchema):
    """
    Схема создания заявки на ипотеку
    """
    booking_id: int = Field(..., description="ID брони", alias="bookingId")
    mortgage_ticket_id: int | None = Field(description="ID заявки на ипотеку", alias="mortgageTicketId")
    values: _ValuesSchema | None = Field(description="Параметры расчета")
    offers: list[SelectedOfferSchema] | None = Field(description="Выбранные предложения")
    client: _ClientSchema | None = Field(description="Персональные данные")
    co_borrowers: _CoBorrowers | None = Field(description="Созаемщики", alias="coBorrowers")

    # todo: move to independent schema for sending to calculator
    documents: _DocumentsSchema | None = Field(description="Документы", default_factory=_DocumentsSchema)
    certificates: list[str | None] | None = Field(description="Сертификаты", default_factory=list)
