from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation

from common.orm.mixins import CreateMixin, ListMixin
from common.loggers.repos import AbstractLogMixin
from ..repos import Booking
from ..entities import BaseBookingRepo


class BookingLog(Model, AbstractLogMixin):
    """
    Лог бронирования
    """

    booking: ForeignKeyNullableRelation[Booking] = fields.ForeignKeyField(
        description="Бронирование",
        model_name="models.Booking",
        on_delete=fields.SET_NULL,
        related_name="booking_logs",
        null=True,
        index=True,
    )

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        table = "booking_bookinglog"


class BookingLogRepo(BaseBookingRepo, CreateMixin, ListMixin):
    """
    Репозиторий лога бронирования
    """

    model = BookingLog
