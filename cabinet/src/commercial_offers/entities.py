from typing import Any

from common.pydantic import CamelCaseBaseModel
from common.orm.entities import BaseRepo


class BaseOfferCamelCaseModel(CamelCaseBaseModel):
    """
    Базовая модель коммерческого предложения в camelCase
    """


class BaseOfferCase:
    """
    Базовый сценарий коммерческого предложения
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseOfferRepo(BaseRepo):
    """
    Базовый репозиторий коммерческого предложения
    """


class BaseOfferPropertyRepo(BaseRepo):
    """
    Базовый репозиторий объекта коммерческого предложения
    """


class BaseOfferSourceRepo(BaseRepo):
    """
    Базовый репозиторий источника коммерческого предложения
    """


class BaseOfferException(Exception):
    """
    Базовая ошибка для городов
    """
    message: str
    status: int
    reason: str
