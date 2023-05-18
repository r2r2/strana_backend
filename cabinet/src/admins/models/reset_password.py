from ..entities import BaseAdminModel


class RequestResetPasswordModel(BaseAdminModel):
    """
    Модель запроса письма редиректа сброса
    """

    class Config:
        orm_mode = True


class ResponseResetPasswordModel(BaseAdminModel):
    """
    Модель ответа письма редиректа сброса
    """

    class Config:
        orm_mode = True
