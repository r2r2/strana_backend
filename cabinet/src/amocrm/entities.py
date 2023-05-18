from typing import Any

from common.orm.entities import BaseRepo


class BaseAmocrmRepo(BaseRepo):
    """
    Базовый репозиторий города
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseAmocrmService:
    """
    Базовый сервис бронирования
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError
