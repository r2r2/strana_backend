from typing import Any

from src.booking.entities import BaseBookingCamelCaseModel


class ResponseBookingDocumentModel(BaseBookingCamelCaseModel):
    id: int
    text: str
    slug: str
    file: dict[str, Any] | None

    class Config:
        orm_mode = True
