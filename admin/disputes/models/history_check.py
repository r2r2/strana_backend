from django.db import models


class CheckHistory(models.Model):
    """
    История проверки
    """

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
        "users.Agency",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='agency_history_check',
        verbose_name='Агентство'
    )
    unique_status: models.ForeignKey = models.ForeignKey(
        to="disputes.UniqueStatus",
        verbose_name="Статус уникальности",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="checks_history",
    )
    created_at = models.DateTimeField(blank=True, null=True, verbose_name='Запрошено')
    term_uid = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='UID условия проверки на уникальность',
    )
    term_comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий к условию проверки на уникальность',
    )
    lead_link = models.TextField(
        blank=True,
        null=True,
        verbose_name='Ссылка на сделку',
    )

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        managed = False
        db_table = "users_checks_history"
        verbose_name = "Проверка"
        verbose_name_plural = "6.3. [Исторические данные] История проверок на уникальность"
        ordering = ["-created_at"]
