import decimal

from ..entities import BaseBookingModel


class RequestLoyaltyRewardModel(BaseBookingModel):
    """
    Модель запроса на применение награды по программе лояльности.
    """

    loyalty_discount_name: str
    loyalty_discount_percent: decimal.Decimal


class ResponseLoyaltyRewardModel(BaseBookingModel):
    """
    Модель ответа на применение награды по программе лояльности.
    """

    ok: bool
