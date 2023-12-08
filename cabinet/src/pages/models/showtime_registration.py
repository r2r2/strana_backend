from ..entities import BasePageModel


class RequestShowtimeRegistrationModel(BasePageModel):
    """
    Модель запроса проверки на уникальность
    """

    class Config:
        orm_mode = True
