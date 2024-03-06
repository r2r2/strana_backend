from common.orm.entities import BaseRepo
from common.pydantic import CamelCaseBaseModel


class BasePrivilegeRepo(BaseRepo):
    """
    Базовый репозиторий программы привилегий
    """


class BasePrivilegeCamelCaseModel(CamelCaseBaseModel):
    """
    Базовая модель программы привилегий
    """


class BasePrivilegeServiceCase:
    """
    Базовый сценарий программы привилегий
    """

    async def __call__(self, *args: list, **kwargs: dict):
        raise NotImplementedError


class BasePrivilegeException(Exception):
    """
    Базовая ошибка программы привилегий
    """

    message: str
    status: int
    reason: str
