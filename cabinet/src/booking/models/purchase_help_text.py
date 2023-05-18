from src.booking.entities import BaseBookingModel


class ResponseHelpTextModel(BaseBookingModel):
    """
    Модель ответа выбора способа покупки
    """

    text: str

    class Config:
        orm_mode = True
