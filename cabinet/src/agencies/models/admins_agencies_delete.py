from ..entities import BaseAgencyModel


class RequestAdminsAgenciesDeleteModel(BaseAgencyModel):
    """
    Модель запроса удаления агентсва администратором
    """

    class Config:
        orm_mode = True


class ResponseAdminsAgenciesDeleteModel(BaseAgencyModel):
    """
    Модель ответа удаления агентсва администратором
    """

    class Config:
        orm_mode = True
