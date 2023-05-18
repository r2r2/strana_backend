from ..entities import BaseBookingModel


class RequestBookingRepeatModel(BaseBookingModel):
    """
    Модель запроса удаления бронирования
    """

    booking_id: int

    class Config:
        orm_mode = True
