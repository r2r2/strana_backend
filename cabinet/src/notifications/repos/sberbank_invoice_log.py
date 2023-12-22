from datetime import datetime

from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from src.notifications.entities import BaseNotificationRepo


class SberbankInvoiceLog(Model):
    """
    Логи отправки чеков оплаты
    """
    id: int = fields.IntField(pk=True)
    amocrm_id: int = fields.IntField(description='ID сделки в AmoCRM', null=True)
    sent_date: datetime = fields.DatetimeField(description='Дата отправки чека')
    sent_email: str = fields.CharField(max_length=64, description='Email, на который отправлен чек', null=True)
    sent_status: bool = fields.BooleanField(description='Статус отправки чека')
    sent_error: str = fields.TextField(description='Ошибка отправки чека', null=True)
    created_at: datetime = fields.DatetimeField(auto_now_add=True, description='Дата создания записи')
    updated_at: datetime = fields.DatetimeField(auto_now=True, description='Дата обновления записи')

    def __str__(self) -> str:
        return f'AMOCRM id:{self.amocrm_id}; Email:{self.sent_email}; Status:{self.sent_status};'

    class Meta:
        table = 'notifications_sberbank_invoice_log'
        table_description = 'Логи отправки чеков оплаты'


class SberbankInvoiceLogRepo(BaseNotificationRepo, CRUDMixin):
    """
    Репозиторий логов отправки чеков оплаты
    """
    model = SberbankInvoiceLog
