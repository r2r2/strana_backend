from typing import Any

from pydantic import BaseModel

from common.orm.entities import BaseRepo


class BaseDocumentModel(BaseModel):
    """
    Базовая модель документа
    """


class BaseDocumentRepo(BaseRepo):
    """
    Базовый репозиторий документа
    """


class BaseDocumentCase(object):
    """
    Базовый сценарий документа
    """

    async def __call__(self, *args: list[Any], **kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError
    

class BaseDocumentException(Exception):
    """
    Базовая ошибка документа
    """

    message: str
    status: int
    reason: str
