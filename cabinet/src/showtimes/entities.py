from typing import Any
from pydantic import BaseModel

from common.orm.entities import BaseRepo


class BaseShowTimeModel(BaseModel):
    """
    Базовая модель записи на показ
    """


class BaseShowTimeRepo(BaseRepo):
    """
    Базовый репозиторий записи на показ
    """


class BaseShowTimeCase(object):
    """
    Базовый сценарий записи на показ
    """

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class BaseShowTimeService(object):
    """
    Базовый сервис записи на показ
    """

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class BaseShowTimeException(Exception):
    """
    Базовая ошибка записи на показ
    """

    message: str
    status: int
    reason: str
