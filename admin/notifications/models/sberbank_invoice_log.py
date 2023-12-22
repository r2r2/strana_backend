from datetime import datetime

from django.db import models


class SberbankInvoiceLog(models.Model):
    """
    Логи отправки чеков оплаты
    """
    amocrm_id: int = models.IntegerField(verbose_name='ID сделки в AmoCRM')
    sent_date: datetime = models.DateTimeField(verbose_name='Дата отправки чека')
    sent_email: str = models.CharField(verbose_name='Email, на который отправлен чек', max_length=64)
    sent_status: bool = models.BooleanField(verbose_name='Статус отправки чека')
    sent_error: str = models.TextField(verbose_name='Ошибка отправки чека', null=True, blank=True)
    created_at: datetime = models.DateTimeField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at: datetime = models.DateTimeField(verbose_name='Дата обновления записи', auto_now=True)

    def __str__(self) -> str:
        return f'AMOCRM id:{self.amocrm_id}; Email:{self.sent_email}; Status:{self.sent_status};'

    class Meta:
        managed = False
        db_table = 'notifications_sberbank_invoice_log'
        verbose_name = 'Лог отправки чека оплаты'
        verbose_name_plural = ' 4.12 Логи отправки чеков оплаты'
