from typing import Any

import structlog

from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BaseCityRepo(BaseRepo):
    """
    Базовый репозиторий города
    """
    logger = structlog.get_logger(__name__)

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseCityService:
    """
    Базовый сервис бронирования
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseCityCase:
    """
    Базовый сценарий городов
    """


class BaseCityModel(CamelCaseBaseModel):
    """
    Базовая модель города
    """

    class Config:
        orm_mode = True


class BaseCityException(Exception):
    """
    Базовая ошибка для городов
    """
    message: str
    status: int
    reason: str
