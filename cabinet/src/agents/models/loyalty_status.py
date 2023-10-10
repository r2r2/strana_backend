from datetime import datetime
from typing import Optional
from pydantic import Field

from ..entities import BaseAgentModel


class LoyaltyStatusModel(BaseAgentModel):
    """
    Модель для получения информации по статусу лояльности.
    """
    loyalty_status_name: str = Field(alias="name")
    loyalty_status_icon: Optional[dict] = Field(default=None, alias="icon")
    loyalty_status_level_icon: Optional[dict] = Field(default=None, alias="level_icon")
    loyalty_status_substrate_card: Optional[dict] = Field(default=None, alias="icon_card")
    loyalty_status_icon_profile: Optional[dict] = Field(default=None, alias="icon_profile")

    class Config:
        orm_mode = True


class BookingLoyaltyModel(BaseAgentModel):
    """
    Модель для передачи информации по бронированию по статусу лояльности.
    """
    amocrm_id: int | None
    point_amount: int | None
    booking_price: int | None

    class Config:
        orm_mode = True
        from_attributes = True


class LoyaltyStatusRequestModel(BaseAgentModel):
    """
    Модель для получения информации по статусу лояльности.
    """
    loyalty_point_amount: int = Field(alias="point_amount")
    date_assignment_loyalty_status: datetime
    loyalty_status: LoyaltyStatusModel
    booking: BookingLoyaltyModel | None

    class Config:
        orm_mode = True
