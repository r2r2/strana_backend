from ..entities import BaseRepresModel


class ResponseAcceptContractModel(BaseRepresModel):
    """
    Модель ответа принятия договора
    """

    class Config:
        orm_mode = True
