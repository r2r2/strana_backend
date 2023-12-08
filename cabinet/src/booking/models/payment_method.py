from typing import Optional

from ..entities import BaseBookingModel
from ..constants import PaymentMethods


class BankContactInfoModel(BaseBookingModel):
    """
    Модель запроса указания данных для связи с банком
    """

    bank_name: str

    class Config:
        orm_mode = True


class RequestPaymentMethodSelectModel(BaseBookingModel):
    """
    Модель запроса выбора способа покупки
    """

    payment_method: PaymentMethods.validator  # todo: payment_method

    maternal_capital: bool
    housing_certificate: bool
    government_loan: bool

    client_has_an_approved_mortgage: Optional[bool]
    bank_contact_info: Optional[BankContactInfoModel]

    class Config:
        orm_mode = True


class ResponsePaymentMethodModel(BaseBookingModel):
    """
    Модель ответа выбора способа покупки
    """

    class Config:
        orm_mode = True


class ResponsePaymentMethodCanBeChangedModel(BaseBookingModel):
    """
    Модель ответа на запрос проверки возможности изменения способа покупки
    """

    can_be_changed: bool
