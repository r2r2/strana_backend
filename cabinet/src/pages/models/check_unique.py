from typing import Optional, Any

from ..entities import BasePageModel


class RequestCheckUniqueModel(BasePageModel):
    """
    Модель запроса проверки на уникальность
    """

    class Config:
        orm_mode = True


class ResponseCheckUniqueModel(BasePageModel):
    """
    Модель ответа проверки на уникальность
    """

    check_image: Optional[dict[str, Any]]
    result_image: Optional[dict[str, Any]]

    class Config:
        orm_mode = True
