from ..entities import BaseBookingModel


class RequestBookingDeleteModel(BaseBookingModel):
    """
    Модель запроса удаления бронирования
    """

    class Config:
        orm_mode = True


class ResponseBookingDeleteModel(BaseBookingModel):
    """
    Модель ответа удаления бронирования
    """

    class Config:
        orm_mode = True
