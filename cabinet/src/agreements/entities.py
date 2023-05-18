from typing import Any

from common.orm.entities import BaseRepo
from pydantic import BaseModel


class BaseAgreementModel(BaseModel):
    """
    Базовая модель документа
    """


class BaseAgreementRepo(BaseRepo):
    """
    Базовый репозиторий документов
    """


class BaseAgreementFilter(BaseModel):
    """
    Базовый фильтр документов
    """


class BaseAgreementCase:
    """
    Базовый сценарий документа
    """

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class BaseAgreementService:
    """
    Базовый сервис документа
    """

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class BaseAgencyException(Exception):
    """
    Базовая ошибка документа
    """

    message: str
    status: int
    reason: str
