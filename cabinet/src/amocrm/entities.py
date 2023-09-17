from typing import Any

from tortoise import Model

from common.orm.entities import BaseRepo


class BaseAmocrmRepo(BaseRepo):
    """
    Базовый репозиторий города
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseAmoCRMDatabaseModel(Model):
    """
    Базовая модель бд AmoCRM
    """


class BaseAmocrmService:
    """
    Базовый сервис бронирования
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError
