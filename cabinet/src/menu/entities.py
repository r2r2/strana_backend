from typing import Any

from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BaseMenuModel(CamelCaseBaseModel):
    """
    Базовая модель меню
    """


class BaseMenuRepo(BaseRepo):
    """
    Базовый репозиторий меню
    """


class BaseMenuCase(object):
    """
    Базовый сценарий меню
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseMenuException(Exception):
    """
    Базовая ошибка меню
    """

    message: str
    status: int
    reason: str
