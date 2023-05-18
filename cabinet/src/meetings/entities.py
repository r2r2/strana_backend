from tortoise import Model

from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BaseMeetingModel(CamelCaseBaseModel):
    """
    Базовая модель встреч
    """
    class Config:
        orm_mode = True


class BaseMeetingDatabaseModel(Model):
    """
    Базовая модель бд для встреч
    """


class BaseMeetingRepo(BaseRepo):
    """
    Базовый репозиторий встреч
    """


class BaseMeetingCase:
    """
    Базовый сценарий встреч
    """


class BaseMeetingService:
    """
    Базовый сервис встреч
    """


class BaseMeetingException(Exception):
    """
    Базовая ошибка для встреч
    """
    message: str
    status: int
    reason: str
