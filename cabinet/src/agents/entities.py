from typing import Any
from pydantic import BaseModel

from common.orm.entities import BaseRepo


class BaseAgentModel(BaseModel):
    """
    Базовая модель агента
    """


class BaseAgentRepo(BaseRepo):
    """
    Базовый репозиторий агента
    """


class BaseAgentCase(object):
    """
    Базовый сценарий агента
    """

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class BaseAgentService(object):
    """
    Базовый сервис агента
    """

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class BaseAgentFilter(BaseModel):
    """
    Базовый фильтр агента
    """


class BaseAgentException(Exception):
    """
    Базовая ошибка агента
    """

    message: str
    status: int
    reason: str
