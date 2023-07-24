from tortoise import Model

from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BaseEventModel(CamelCaseBaseModel):
    """
    Базовая модель мероприятий
    """
    class Config:
        orm_mode = True


class BaseEventDatabaseModel(Model):
    """
    Базовая модель бд для мероприятий
    """


class BaseEventRepo(BaseRepo):
    """
    Базовый репозиторий мероприятий
    """


class BaseEventCase:
    """
    Базовый сценарий мероприятий
    """


class BaseEventService:
    """
    Базовый сервис мероприятий
    """


class BaseEventException(Exception):
    """
    Базовая ошибка для мероприятий
    """
    message: str
    status: int
    reason: str
