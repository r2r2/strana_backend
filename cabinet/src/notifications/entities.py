from typing import Any

from pydantic import BaseModel

from common.orm.entities import BaseRepo


class BaseNotificationModel(BaseModel):
    """
    Базовая модель уведомления
    """


class BaseNotificationRepo(BaseRepo):
    """
    Базовый репозиторий уведомления
    """


class BaseNotificationCase(object):
    """
    Базовый сценарий уведомления
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseNotificationManager(object):
    """
    Базовый менеджер уведомления
    """


class BaseNotificationException(Exception):
    """
    Базовая ошибка уведомления
    """

    message: str
    status: int
    reason: str


class BaseNotificationService:
    """
    Базовый сервис уведомлений
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError
