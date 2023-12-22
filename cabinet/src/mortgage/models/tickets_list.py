from typing import Any

from pydantic import Field, root_validator

from src.mortgage.entities import BaseMortgageCamelCaseSchema


class MortgageCalculatorConditionSchema(BaseMortgageCamelCaseSchema):
    id: int
    cost_before: float | None = Field(description="Стоимость до")
    initial_fee_before: float | None = Field(description="Первоначальный взнос до, %")
    until: float | None = Field(description="Срок до, лет")
    initial_payment: Any = Field(description="Первоначальный взнос, руб")

    @root_validator
    def validate_initial_payment(cls, values):
        cost = values.get('cost_before')
        initial_fee = values.get('initial_fee_before')
        if cost and initial_fee:
            values['initial_payment'] = cost * (initial_fee / 100)
        return values


class AmocrmStatusSchema(BaseMortgageCamelCaseSchema):
    id: int
    name: str | None = Field(description="Название статуса")


class MortgageApplicationStatusSchema(BaseMortgageCamelCaseSchema):
    id: int
    name: str | None = Field(description="Название статуса")


class TicketsResponseSchema(BaseMortgageCamelCaseSchema):
    id: int
    booking_id: int = Field(description="ID бронирования")
    rate: Any = Field(description="Процентная ставка")
    calculator_condition: MortgageCalculatorConditionSchema | None = Field(description="Условие в калькуляторе")
    status: MortgageApplicationStatusSchema | None = Field(description="Статус заявки")


class MortgageTicketsResponseSchema(BaseMortgageCamelCaseSchema):
    statuses: list[MortgageApplicationStatusSchema] = Field(description="Статусы заявки")
    tickets: list[TicketsResponseSchema] = Field(description="Заявки")
