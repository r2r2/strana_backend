from typing import Any
from pydantic import BaseModel
from tortoise import Model

from common.models import TimeBasedMixin
from common.orm.entities import BaseRepo


class BaseTaskModel(Model, TimeBasedMixin):
    """
    Базовая модель задачи
    """


class BaseTaskSchema(BaseModel):
    """
    Базовая схема задачи
    """


class BaseTaskRepo(BaseRepo):
    """
    Базовый репозиторий задачи
    """


class BaseTaskFilter(BaseModel):
    """
    Базовый фильтр задачи
    """


class BaseTaskCase:
    """
    Базовый сценарий задачи
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseTaskService:
    """
    Базовый сервис задач
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseTaskException(Exception):
    """
    Базовая ошибка задачи
    """

    message: str
    status: int
    reason: str
