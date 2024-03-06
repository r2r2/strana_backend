from datetime import datetime

from pydantic import Field

from src.mortgage.entities import BaseMortgageSchema


class ArchiveTicketStatusSchema(BaseMortgageSchema):
    """
    Схема архивного статуса заявки на ипотеку
    """
    booking_id: int = Field(..., description="ID брони")
    external_code: int = Field(..., description="ID заявки в ИК")
    mortgage_application_status_until: str = Field(..., description="Статус заявки на ипотеку До")
    mortgage_application_status_after: str = Field(..., description="Статус заявки на ипотеку После")
    status_change_date: datetime = Field(..., description="Время изменения статуса")
    is_created: bool = Field(..., description="Флаг создания записи")
