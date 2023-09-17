from ..entities import BaseBookingCamelCaseModel


class RequestCreateBookingModel(BaseBookingCamelCaseModel):
    """
    Модель запроса создания сделки
    """
    property_global_id: str
    property_slug: str
    booking_type_id: int
