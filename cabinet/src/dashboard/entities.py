from typing import Any

from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BaseDashboardRepo(BaseRepo):
    """
    Базовый репозиторий главной страницы
    """
    pass


class BaseDashboardCase:
    """
    Базовый сценарий главной страницы
    """
    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseDashboardModel(CamelCaseBaseModel):
    """
    Базовая модель главной страницы
    """
    pass


class BaseDashboardException(Exception):
    """
    Базовая ошибка бронирования
    """

    message: str
    status: int
    reason: str

