from ..entities import BaseAgentModel


class RequestChangePhoneModel(BaseAgentModel):
    """
    Модель запроса смены телефона
    """

    class Config:
        orm_mode = True


class ResponseChangePhoneModel(BaseAgentModel):
    """
    Модель ответа смены телефона
    """

    class Config:
        orm_mode = True
