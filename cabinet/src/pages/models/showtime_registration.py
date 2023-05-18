from typing import Optional, Any

from ..entities import BasePageModel


class RequestShowtimeRegistrationModel(BasePageModel):
    """
    Модель запроса проверки на уникальность
    """

    class Config:
        orm_mode = True


class ResponseShowtimeRegistrationModel(BasePageModel):
    """
    Модель ответа проверки на уникальность
    """

    result_image: Optional[dict[str, Any]]

    class Config:
        orm_mode = True
