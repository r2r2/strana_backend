from django.db import models

from common import TimeBasedMixin


class PrivilegeFeedbackEmail(TimeBasedMixin, models.Model):
    """
    Emails для результатов формы "Программа привилегий"
    """
    email: str = models.CharField(max_length=250, verbose_name="Email")
    full_name: str = models.CharField(max_length=250, verbose_name="ФИО клиента", blank=True)
    feedback_settings: models.ForeignKey = models.ForeignKey(
        to="settings.FeedbackSettings",
        related_name="privilege_emails",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Использовать в настройках",
    )

    def __str__(self) -> str:
        return self.email

    class Meta:
        managed = False
        db_table = 'privilege_feedback_email'
        verbose_name = 'Emails для результатов формы "Программа привилегий"'
        verbose_name_plural = '22.9 Emails для результатов формы "Программа привилегий"'

    def __repr__(self):
        return self.email

