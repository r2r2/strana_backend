from typing import Any

from pydantic import BaseModel

from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BaseMortgageSchema(BaseModel):
    """
    Базовая схема заявки на ипотеку
    """

    class Config:
        orm_mode = True


class BaseMortgageCamelCaseSchema(CamelCaseBaseModel):
    """
    Базовая схема заявки на ипотеку в camelCase
    """

    class Config:
        orm_mode = True


class BaseMortgageCase:
    """
    Базовый сценарий задачи
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseMortgageService:
    """
    Базовый сервис задач
    """

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class BaseMortgageException(Exception):
    """
    Базовая ошибка заявки на ипотеку
    """

    message: str
    status: int
    reason: str


class BaseMortgageRepo(BaseRepo):
    """
    Базовый репозиторий заявки на ипотеку
    """
