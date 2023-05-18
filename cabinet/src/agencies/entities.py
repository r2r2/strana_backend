from typing import Any
from pydantic import BaseModel

from common.orm.entities import BaseRepo


class BaseAgencyModel(BaseModel):
    """
    Базовая модель агенства
    """


class BaseAgencyRepo(BaseRepo):
    """
    Базовый репозиторий агенства
    """


class BaseAgencyCase(object):
    """
    Базовый сценарий агенства
    """

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class BaseAgencyService(object):
    """
    Базовый сервис агенства
    """

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class BaseAgencyFilter(BaseModel):
    """
    Базовый фильтр агенства
    """


class BaseAgencyException(Exception):
    """
    Базовая ошибка агенства
    """

    message: str
    status: int
    reason: str
