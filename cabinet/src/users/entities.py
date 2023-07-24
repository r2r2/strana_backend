from typing import Any, Type

from celery.local import PromiseProxy
from common.entities import BaseFilter
from common.orm.entities import BaseRepo
from pydantic import BaseModel
from common.pydantic import CamelCaseBaseModel


class BaseUserModel(BaseModel):
    """
    Базовая модель пользователя
    """

class BaseUserCamelCaseModel(CamelCaseBaseModel):
    """
    Базовая модель пользователя CamelCase
    """


class BaseUserFilter(BaseFilter):
    """
    Базовый фильтр пользователя
    """


class BaseUserRepo(BaseRepo):
    """
    Базовый репозиторий пользователя
    """


class BaseUserCase:
    """
    Базовый сценарий пользователя
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseProcessLoginCase(BaseUserCase):
    _NotFoundError: Type[Exception]
    _WrongPasswordError: Type[Exception]
    _NotApprovedError: Type[Exception]

    _import_clients_task: PromiseProxy

    async def _import_amocrm_hook(self, user: "User"):
        """Abstract method for amocrm integration"""

    async def __call__(self, *args, **kwargs):
        raise NotImplementedError


class BaseUserService:
    """
    Базовый сервис пользователя
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseUserException(Exception):
    """
    Базовая ошибка пользователя
    """

    message: str
    status: int
    reason: str


class BaseCheckModel(CamelCaseBaseModel):
    """
    базовая модель проверки
    """


class BaseCheckCase:
    """
    базовый сценарий проверки
    """
    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseCheckException(Exception):
    """
    Базовая ошибка проверки
    """
    message: str
    status: int
    reason: str


class BaseManagerModel(BaseModel):
    """
    Базовая модель менеджера
    """


class BaseManagerFilter(BaseModel):
    """
    Базовый фильтр пользователя
    """


class BaseManagerRepo(BaseModel):
    """
    Базовый репозиторий менеджера
    """


class BaseManagerCase:
    """
    Базовый сценарий менеджера
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError


class BaseManagerException(Exception):
    """
    Базовая ошибка менеджера
    """

    message: str
    status: int
    reason: str
