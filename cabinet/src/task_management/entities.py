from datetime import datetime
from typing import Any, Optional
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


class TaskContextDTO:
    __slots__ = ('status_slug', 'meeting_new_date')

    class __TaskContextDTO(BaseModel):
        status_slug: Optional[str]
        meeting_new_date: Optional[datetime]

    def __init__(self):
        self.status_slug: Optional[str] = None
        self.meeting_new_date: Optional[datetime] = None

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __setattr__(self, key, value):
        self.__TaskContextDTO(**{key: value})
        super().__setattr__(key, value)

    def to_dict(self) -> dict[str, Any]:
        return {attr: getattr(self, attr) for attr in self.__slots__}
