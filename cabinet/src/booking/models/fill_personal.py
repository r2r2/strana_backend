from typing import Optional
from ..entities import BaseBookingModel


class RequestFillPersonalModel(BaseBookingModel):
    """
    Модель запроса заполнения персональных данных
    """
    personal_filled: bool
    email_force: Optional[bool] = False

    class Config:
        orm_mode = True


class ResponseFillPersonalModel(BaseBookingModel):
    """
    Модель ответа заполнения персональных данных
    """

    id: int

    class Config:
        orm_mode = True
