from typing import Optional, Any
from pydantic import Field

from ..entities import BaseDocumentModel


class _InteractionDocumentModel(BaseDocumentModel):
    
    name: str
    icon: Any
    file: Any

class ResponseGetInteractionDocument(BaseDocumentModel):
    """
    Модель ответа по взаимодействию.
    """
    count: int
    page_info: dict[str, Any]
    result: list[_InteractionDocumentModel]
    
    class Config:
        orm_mode = True