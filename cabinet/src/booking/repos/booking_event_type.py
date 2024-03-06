from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from src.booking.entities import BaseBookingRepo


class BookingEventType(Model):
    id: int = fields.IntField(description="ID", pk=True)
    event_type_name: str = fields.CharField(description="Название", max_length=150)
    slug: str = fields.CharField(description="Слаг", max_length=100)

    def __str__(self) -> str:
        return f"<{self.event_type_name}>"

    class Meta:
        table = "booking_event_type"


class BookingEventTypeRepo(BaseBookingRepo, CRUDMixin):
    """
    Репозитория типов событий бронирования
    """

    model = BookingEventType

