from typing import Any

from pydantic import BaseModel
from tortoise import Model

from common.orm.entities import BaseRepo


class BasePaymentModel(BaseModel):
    """
    Базовая модель способа оплаты
    """


class BasePaymentDatabaseModel(Model):
    """
    Базовая модель бд способа оплаты
    """


class BasePaymentRepo(BaseRepo):
    """
    Базовый репозиторий способа оплаты
    """


class BasePaymentCase:
    """
    Базовый сценарий способа оплаты
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BasePaymentService:
    """
    Базовый сервис способа оплаты
    """
    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BasePaymentException(Exception):
    """
    Базовая ошибка способа оплаты
    """
    message: str
    status: int
    reason: str
