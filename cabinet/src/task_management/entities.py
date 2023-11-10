from typing import Any
from pydantic import BaseModel, Extra
from tortoise import Model

from common.models import TimeBasedMixin
from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BaseTaskModel(Model, TimeBasedMixin):
    """
    Базовая модель задачи
    """


class BaseTaskSchema(BaseModel):
    """
    Базовая схема задачи
    """


class BaseTaskCamelCaseSchema(CamelCaseBaseModel):
    """
    Базовая схема задачи в camelCase
    """
    class Config:
        orm_mode = True


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

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class BaseTaskException(Exception):
    """
    Базовая ошибка задачи
    """

    message: str
    status: int
    reason: str


class BaseTaskContextDTO(BaseModel, extra=Extra.forbid, validate_assignment=True):
    """
    Базовая модель контекста задачи
    """

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)
