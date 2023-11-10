from django.db import models


class LogSms(models.Model):
    """
    Логи смс сообщений.
    """

    text = models.TextField(
        verbose_name="Текст смс сообщения",
        null=True,
        blank=True,
    )
    lk_type: str = models.CharField(
        verbose_name="Сервис ЛК, в котором отправлено смс сообщение",
        max_length=10,
        null=True,
        blank=True,
    )
    sms_event_slug = models.CharField(
        max_length=100,
        verbose_name="Слаг события отправки смс",
        null=True,
        blank=True,
    )
    recipient_phone = models.CharField(
        verbose_name="Номер телефона получателя",
        max_length=20,
        null=True,
        blank=True,
    )
    is_sent = models.BooleanField(
        verbose_name="Сообщение отправлено",
        default=False,
    )
    created_at = models.DateTimeField(verbose_name="Когда создано", help_text="Когда создано", auto_now_add=True)

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        db_table = "common_log_sms_notification"
        verbose_name = "Лог смс сообщений"
        verbose_name_plural = " 4.4. [Логи] Логи смс сообщений"
