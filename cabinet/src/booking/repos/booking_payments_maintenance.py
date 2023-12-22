from tortoise import Model, fields
from datetime import datetime

from common.orm.mixins import CountMixin, CRUDMixin

from ..entities import BaseBookingRepo


class BookingPaymentsMaintenance(Model):
    """
    Данные по успешным оплатам по бронированию
    """

    id: int = fields.IntField(description="ID", pk=True)
    booking_amocrm_id: int = fields.BigIntField(description="ID в AmoCRM")
    successful_payment: bool = fields.BooleanField(description="Успешная оплата")
    created_at: datetime = fields.DatetimeField(description="Дата и время создания", auto_now_add=True)

    def __str__(self) -> str:
        return str(self.booking_amocrm_id)

    class Meta:
        table = "bookings_payments_maintenance"


class BookingPaymentsMaintenanceRepo(BaseBookingRepo, CRUDMixin, CountMixin):
    """
    Репозиторий данных по успешным оплатам
    """

    model = BookingPaymentsMaintenance
