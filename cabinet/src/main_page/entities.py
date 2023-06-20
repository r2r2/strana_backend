from typing import Any

from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BaseMainPageRepo(BaseRepo):
    """
    Базовый репозиторий главной страницы
    """
    pass


class BaseMainPageCase:
    """
    Базовый сценарий главной страницы
    """
    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseMainPageModel(CamelCaseBaseModel):
    """
    Базовая модель главной страницы
    """
    pass


class BaseMainPageException(Exception):
    """
    Базовая ошибка бронирования
    """

    message: str
    status: int
    reason: str

