from datetime import datetime

from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from src.booking.entities import BaseBookingRepo


class MortgageApplicationArchive(Model):
    id: int = fields.IntField(description="ID", pk=True)
    external_code: int = fields.IntField(description="ID заявки в ИК")
    booking_id: int = fields.IntField(description="ID брони")
    mortgage_application_status_until: str = fields.CharField(
        description="Статус заявки на ипотеку До",
        max_length=150
    )
    mortgage_application_status_after: str = fields.CharField(
        description="Статус заявки на ипотеку После",
        max_length=150
    )
    status_change_date: datetime = fields.DatetimeField(
        description="Время изменения статуса",
        auto_now=True
    )

    def __str__(self) -> str:
        return f"<{self.id}| Booking_id: {self.booking_id}>"

    class Meta:
        table = "mortgage_application_archive"


class MortgageApplicationArchiveRepo(BaseBookingRepo, CRUDMixin):
    """
    Репозитория архива заявок на ипотеку
    """
    model = MortgageApplicationArchive
