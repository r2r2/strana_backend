from typing import Any

from pydantic import BaseModel

from common.orm.entities import BaseRepo


class BasePageModel(BaseModel):
    """
    Базовая модель страницы
    """


class BasePageRepo(BaseRepo):
    """
    Базовый репозиторий страницы
    """


class BasePageCase(object):
    """
    Базовый сценарий страницы
    """

    async def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError
