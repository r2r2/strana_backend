from tortoise import Model

from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BaseTextBlockModel(CamelCaseBaseModel):
    """
    Базовая модель текстовых блоков
    """
    class Config:
        orm_mode = True


class BaseTextBlockDatabaseModel(Model):
    """
    Базовая модель бд для текстовых блоков
    """


class BaseTextBlockRepo(BaseRepo):
    """
    Базовый репозиторий текстовых блоков
    """


class BaseTextBlockCase:
    """
    Базовый сценарий текстовых блоков
    """


class BaseTextBlockService:
    """
    Базовый сервис текстовых блоков
    """


class BaseTextBlockException(Exception):
    """
    Базовая ошибка для текстовых блоков
    """
    message: str
    status: int
    reason: str
