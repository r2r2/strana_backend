from typing import Any
from pydantic import BaseModel

from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BaseBookingModel(BaseModel):
    """
    Базовая модель бронирования
    """


class BaseBookingCamelCaseBaseModel(CamelCaseBaseModel):
    """
    Базовая модель бронирования в camelCase
    """


class BaseBookingRepo(BaseRepo):
    """
    Базовый репозиторий бронирования
    """


class BaseBookingFilter(BaseModel):
    """
    Базовый фильтр бронирования
    """


class BaseBookingCase(object):
    """
    Базовый сценарий бронирования
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseBookingPayment(object):
    """
    Базовый платеж бронирования
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseBookingService(object):
    """
    Базовый сервис бронирования
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseBookingException(Exception):
    """
    Базовая ошибка бронирования
    """

    message: str
    status: int
    reason: str


class BaseBookingBuildingTypeListCase(object):
    """
    Базовый сценарий списка условий оплаты
    """
    async def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError


class BaseBookingBuildingTypeModel(CamelCaseBaseModel):
    """
    Базовая модель условий оплаты
    """