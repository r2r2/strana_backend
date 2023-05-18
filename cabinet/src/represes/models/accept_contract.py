from ..entities import BaseRepresModel


class RequestAcceptContractModel(BaseRepresModel):
    """
    Модель запроса принятия договора
    """

    is_contracted: bool

    class Config:
        orm_mode = True


class ResponseAcceptContractModel(BaseRepresModel):
    """
    Модель ответа принятия договора
    """

    class Config:
        orm_mode = True
