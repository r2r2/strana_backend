from ..entities import BaseRepresModel


class RequestChangePhoneModel(BaseRepresModel):
    """
    Модель запроса смены телефона
    """

    class Config:
        orm_mode = True


class ResponseChangePhoneModel(BaseRepresModel):
    """
    Модель ответа смены телефона
    """

    class Config:
        orm_mode = True
