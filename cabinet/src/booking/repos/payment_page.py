from tortoise import fields

from common.orm.mixins import RetrieveMixin
from ..entities import BaseBookingRepo, BaseBookingDatabaseModel


class PaymentPageNotification(BaseBookingDatabaseModel):
    """
    Уведомления страницы успешной оплаты
    """
    id: int = fields.IntField(description="ID", pk=True)
    title: str = fields.CharField(max_length=50, description="Заголовок")
    notify_text: str = fields.TextField(description="Текст уведомления")
    button_text: str = fields.CharField(max_length=50, description="Текст кнопки")

    class Meta:
        table = "booking_payment_page_notifications"


class PaymentPageNotificationRepo(BaseBookingRepo, RetrieveMixin):
    """
    Репозиторий уведомления страницы успешной оплаты
    """
    model = PaymentPageNotification
