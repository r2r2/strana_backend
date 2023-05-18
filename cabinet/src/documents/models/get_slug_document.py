from typing import Optional, Any

from ..entities import BaseDocumentModel


class RequestGetSlugDocumentModel(BaseDocumentModel):
    """
    Модель запроса получения документапо слагу
    """

    class Config:
        orm_mode = True


class ResponseGetSlugEscrowDocumentModel(BaseDocumentModel):
    """
    Модель ответа получения памятки эскроу
    """

    slug: str
    file: Optional[dict[str, Any]]

    class Config:
        orm_mode = True


class ResponseGetSlugDocumentModel(ResponseGetSlugEscrowDocumentModel):
    """
    Модель ответа получения документа по слагу
    """

    text: str
