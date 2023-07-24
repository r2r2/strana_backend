from django.db import models


class HistoricalDisputeData(models.Model):
    """
    Учет исторических данных оспаривания
    """
    dispute_agent = models.ForeignKey(
        "users.CabinetUser",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='historical_dispute_data_dispute_agent',
        verbose_name='Оспаривающий агент'
    )
    dispute_agent_agency = models.ForeignKey(
        "users.Agency",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='historical_dispute_data_agent_agency',
        verbose_name='Агентство оспаривающего агента',
        help_text='Агентство, которое в настоящее время закреплено за клиентом',
    )
    client = models.ForeignKey(
        "users.CabinetUser",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='historical_dispute_data_client',
        verbose_name='Клиент',
        help_text='Проверяемый клиент',
    )
    agent = models.ForeignKey(
        "users.CabinetUser",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='historical_dispute_data_agent',
        verbose_name='Текущий агент',
        help_text='Агент, который в настоящее время закреплен за клиентом',
    )
    client_agency = models.ForeignKey(
        "users.Agency",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='historical_dispute_data_client_agency',
        verbose_name='Текущее агентство клиента',
        help_text='Агентство, которое в настоящее время закреплено за клиентом',
    )
    dispute_requested = models.DateTimeField(blank=True, null=True, verbose_name='Время оспаривания')
    admin = models.ForeignKey(
        "users.CabinetUser",
        models.DO_NOTHING,
        blank=True,
        null=True,
        related_name='historical_dispute_data_admin',
        verbose_name='Обновлено администратором'
    )
    admin_update = models.DateTimeField(blank=True, null=True, verbose_name='Дата обновления статуса администратором')
    admin_unique_status: models.ForeignKey = models.ForeignKey(
        to="disputes.UniqueStatus",
        verbose_name="Статус уникальности",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="historical_dispute_data_admin_unique_status",
    )

    def __str__(self):
        return f"{self.client} - {self.agent} - {self.dispute_agent}"

    class Meta:
        managed = False
        db_table = 'historical_dispute_data'
        verbose_name = 'История оспаривания'
        verbose_name_plural = '2.7. [Справочник] История оспаривания'
