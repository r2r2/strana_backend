from typing import Any
from pydantic import BaseModel

from common.orm.entities import BaseRepo


class BaseRepresModel(BaseModel):
    """
    Базовая модель представителя
    """


class BaseRepresRepo(BaseRepo):
    """
    Базовый репозиторий представителя
    """


class BaseRepresCase(object):
    """
    Базовый сценарий представителя
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseRepresService(object):
    """
    Базовый сервис представителя
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseRepresException(Exception):
    """
    Базовая ошибка представителя
    """

    message: str
    status: int
    reason: str
