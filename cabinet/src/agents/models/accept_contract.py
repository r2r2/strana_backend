from ..entities import BaseAgentModel


class RequestAcceptContractModel(BaseAgentModel):
    """
    Модель запроса принятия договора
    """

    is_contracted: bool

    class Config:
        orm_mode = True


class ResponseAcceptContractModel(BaseAgentModel):
    """
    Модель ответа принятия договора
    """

    class Config:
        orm_mode = True
