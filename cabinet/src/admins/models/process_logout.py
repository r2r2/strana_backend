from ..entities import BaseAdminModel


class RequestProcessLogoutModel(BaseAdminModel):
    """
    Модель запроса процессинга выхода
    """

    class Config:
        orm_mode = True


class ResponseProcessLogoutModel(BaseAdminModel):
    """
    Модель ответа процессинга выхода
    """

    class Config:
        orm_mode = True
