from decimal import Decimal
from typing import Literal, Optional, Union

from ..entities import BaseBookingModel


class _LeadWebhookCustomFieldValueModel(BaseBookingModel):
    """
    Модель значения кастомного поля заявки вебъука АМО
    """

    enum: Union[int, str]
    value: Union[int, str, float, Decimal]

    class Config:
        orm_mode = True


class _LeadWebhookCustomFieldModel(BaseBookingModel):
    """
    Модель кастомного поля заявки вебхука АМО
    """

    id: Union[int, str]
    name: Optional[str]
    values: list[Union[str, int, _LeadWebhookCustomFieldValueModel]]

    class Config:
        orm_mode = True


class _LeadWebhookModel(BaseBookingModel):
    """
    Модель заявки вебхука АМО
    """

    id: Union[int, str]
    status_id: Union[int, str]
    old_status_id: Union[int, str]
    custom_fields: Optional[list[_LeadWebhookCustomFieldModel]]

    class Config:
        orm_mode = True


class RequestAmoCRMWebhookModel(BaseBookingModel):
    """
    Модель запроса вебхука АМО
    """

    leads: dict[Literal["status", "update", "create", "add"], dict[Literal["0"], _LeadWebhookModel]]

    class Config:
        orm_mode = True


class ResponseAmoCRMWebhookModel(BaseBookingModel):
    """
    Модель ответ вебхука АМО
    """

    id: int

    class Config:
        orm_mode = True
