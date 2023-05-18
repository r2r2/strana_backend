from typing import Optional, Any

from ..entities import BaseTipModel


class RequestTipListModel(BaseTipModel):
    """
    Модель запроса списка подсказок
    """

    class Config:
        orm_mode = True


class _TipListModel(BaseTipModel):
    """
    Модель списка подсказок
    """

    id: int
    image: Optional[dict[str, Any]]
    title: Optional[str]
    text: Optional[str]
    order: Optional[int]

    class Config:
        orm_mode = True


class ResponseTipListModel(BaseTipModel):
    """
    Модель ответа списка подсказок
    """

    count: int
    result: Optional[list[_TipListModel]]

    class Config:
        orm_mode = True
