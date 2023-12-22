from django.db import models


class MortgageApplicationStatus(models.Model):
    """
    Статусы заявки на ипотеку через застройщика.
    """
    name: str = models.CharField(max_length=255, verbose_name="Название статуса")
    priority: int = models.IntegerField(verbose_name="Приоритет", default=0)
    amocrm_statuses: models.ManyToManyField = models.ManyToManyField(
        "booking.AmocrmStatus",
        through="MortgageApplicationStatusAmocrmStatusesThrough",
        verbose_name="Статусы сделки",
        related_name="mortgage_application_statuses",
        blank=True,
        through_fields=("mortgage_application_status", "amocrm_status"),
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = 'mortgage_application_status'
        verbose_name = "Статус заявки"
        verbose_name_plural = "21.3 Статусы заявки на ипотеку через застройщика"


class MortgageApplicationStatusAmocrmStatusesThrough(models.Model):
    """
    Промежуточная таблица статусов заявки на ипотеку через застройщика к статусам сделок.
    """
    mortgage_application_status: models.ForeignKey = models.ForeignKey(
        to="MortgageApplicationStatus",
        on_delete=models.CASCADE,
        related_name="mortgage_application_status_amocrm_statuses_through",
    )
    amocrm_status: models.ForeignKey = models.ForeignKey(
        to="booking.AmocrmStatus",
        on_delete=models.CASCADE,
        related_name="mortgage_application_status_amocrm_statuses_through",
    )

    class Meta:
        managed = False
        db_table = 'mortgage_application_status_amocrm_statuses_through'
