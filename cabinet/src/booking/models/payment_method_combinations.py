from typing import Literal

from ..entities import BaseBookingModel


class PaymentMethodCombination(BaseBookingModel):
    payment_method: Literal["cash", "mortgage", "installment_plan"]
    maternal_capital: bool
    government_loan: bool
    housing_certificate: bool


class ResponsePaymentMethodCombinationsModel(BaseBookingModel):
    combinations: list[PaymentMethodCombination]
