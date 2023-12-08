from django.db import models


class PaymentPageNotification(models.Model):
    """
    Уведомления страницы успешной оплаты
    """
    title: str = models.CharField(max_length=50, verbose_name="Заголовок")
    notify_text: str = models.TextField(verbose_name="Текст уведомления")
    button_text: str = models.CharField(max_length=50, verbose_name="Текст кнопки")
    slug: str = models.CharField(max_length=100, verbose_name="Slug источника", null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = "booking_payment_page_notifications"
        verbose_name = "Уведомление"
        verbose_name_plural = "13.3. [Общее] Уведомления страниц оплаты"
