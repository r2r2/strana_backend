from typing import Optional, Any

from ..entities import BaseDocumentModel


class RequestGetDocumentModel(BaseDocumentModel):
    """
    Модель запроса получения документа
    """

    class Config:
        orm_mode = True


class ResponseGetEscrowDocumentModel(BaseDocumentModel):
    """
    Модель ответа получения памятки эскроу
    """

    slug: str
    file: Optional[dict[str, Any]]

    class Config:
        orm_mode = True


class ResponseGetDocumentModel(ResponseGetEscrowDocumentModel):
    """
    Модель ответа получения документа
    """

    text: str

    class Config:
        orm_mode = True
