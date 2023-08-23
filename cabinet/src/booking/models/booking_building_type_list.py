from typing import Optional

from src.booking.entities import BaseBookingBuildingTypeModel


class BookingBuildingTypeDetailResponse(BaseBookingBuildingTypeModel):
    """
    Модель ответа условий оплаты
    """
    id: int
    price: int
    amocrm_id: int
    period: int
    priority: Optional[int]
