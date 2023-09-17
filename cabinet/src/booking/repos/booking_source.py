from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from src.booking.entities import BaseBookingRepo


class BookingSource(Model):
    id: int = fields.IntField(description="ID", pk=True)
    name: str = fields.CharField(max_length=100, description="Название источника")
    slug: str = fields.CharField(max_length=100, description="Слаг источника")

    taskchains: fields.ManyToManyRelation["TaskChain"]
    bookings: fields.ReverseRelation["Booking"]

    def __str__(self):
        return self.name

    class Meta:
        table = "booking_source"


class BookingSourceRepo(BaseBookingRepo, CRUDMixin):
    """
    Репозиторий источника бронирования
    """
    model = BookingSource
