from typing import Any

from common.pydantic import CamelCaseBaseModel


class BaseMainPageModel(CamelCaseBaseModel):
    """
    Базовая модель главной страницы
    """


class BaseMainPageCase(object):
    """
    Базовый кейс главной страницы
    """
    async def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError


class BaseManagerException(Exception):
    """
    Базовая ошибка менеджера главной страницы
    """

    message: str
    status: int
    reason: str
