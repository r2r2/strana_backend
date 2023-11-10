from django.db import models


class LogEmail(models.Model):
    """
    Логи писем.
    """

    topic = models.TextField(
        verbose_name="Заголовок письма",
        null=True,
        blank=True,
    )
    text = models.TextField(
        verbose_name="Текст письма",
        null=True,
        blank=True,
    )
    lk_type: str = models.CharField(
        verbose_name="Сервис ЛК, в котором отправлено письмо",
        max_length=10,
        null=True,
        blank=True,
    )
    mail_event_slug = models.CharField(
        max_length=100,
        verbose_name="Слаг назначения события отправки письма",
        null=True,
        blank=True,
    )
    recipient_emails = models.TextField(
        verbose_name="Почтовые адреса получателей письма",
        null=True,
        blank=True,
    )
    is_sent = models.BooleanField(
        verbose_name="Письмо отправлено",
        default=False,
    )
    created_at = models.DateTimeField(verbose_name="Когда создано", help_text="Когда создано", auto_now_add=True)

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        db_table = "common_log_email_notification"
        verbose_name = "Лог письма"
        verbose_name_plural = " 4.3. [Справочник] Логи писем"
