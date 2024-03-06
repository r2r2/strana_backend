from tortoise import Model, fields

from typing import TYPE_CHECKING

from common.orm.mixins import CRUDMixin
from src.booking.entities import BaseBookingRepo

if TYPE_CHECKING:
    from src.booking.repos import BookingEventType


class BookingEvent(Model):
    id: int = fields.IntField(description="ID", pk=True)
    event_name: str = fields.CharField(description="Название", max_length=150)
    event_description: str = fields.TextField(description="Описание", null=True)
    slug: str = fields.CharField(description="Слаг", max_length=100)
    event_type: fields.ForeignKeyRelation["BookingEventType"] = fields.ForeignKeyField(
        description="Тип события",
        model_name="models.BookingEventType",
        related_name="event",
        on_delete=fields.CASCADE,
        null=True
    )

    def __str__(self) -> str:
        return f"<{self.event_name}>"

    class Meta:
        table = "booking_event"


class BookingEventRepo(BaseBookingRepo, CRUDMixin):
    """
    Репозиторий событий бронирования
    """

    model = BookingEvent
