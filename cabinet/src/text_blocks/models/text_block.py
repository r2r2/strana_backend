from typing import Optional

from ..entities import BaseTextBlockModel


class ResponseTextBlockModel(BaseTextBlockModel):
    """
    Модель ответа получения текстового блока.
    """
    title: Optional[str]
    text: Optional[str]
