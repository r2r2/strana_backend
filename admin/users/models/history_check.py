from django.db import models
from django.utils.translation import gettext_lazy as _


class CheckHistory(models.Model):
    """
    История проверки
    """

    class StatusCheck(models.TextChoices):
        """
        Статус проверки
        """
        UNIQUE: str = "unique", _("Уникальный")
        NOT_UNIQUE: str = "not_unique", _("Неуникальный")
        CAN_DISPUTE = "can_dispute", _("Закреплен, но можно оспорить")
        ERROR: str = 'error', _("Ошибка")

    client = models.ForeignKey(
        "users.CabinetUser",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='user_history_check',
        verbose_name='Клиент'
    )
    client_phone = models.CharField(
        unique=False,
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Номер телефона',
        help_text='Номер телефона'
    )
    agent = models.ForeignKey(
        "users.CabinetUser",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='agent_history_check',
        verbose_name='Агент'
    )
    agency = models.ForeignKey(
        "agencies.Agency",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='agency_history_check',
        verbose_name='Агентство'
    )
    status = models.CharField(choices=StatusCheck.choices, max_length=50, verbose_name='Статус проверки')
    created_at = models.DateTimeField(blank=True, null=True, verbose_name='Запрошено')

    def __str__(self) -> str:
        return self.status if self.status else str(self.id)

    class Meta:
        managed = False
        db_table = "users_checks_history"
        verbose_name = "Проверка"
        verbose_name_plural = "История проверок"
        ordering = ["status", "created_at"]
