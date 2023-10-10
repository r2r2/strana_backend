from django.db import models


class DisputeStatus(models.Model):
    """
    Таблица статусов оспаривания
    """

    title: str = models.CharField(verbose_name="Название", max_length=255)

    def __str__(self) -> str:
        return self.title

    class Meta:
        managed = False
        db_table = "users_dispute_statuses"
        verbose_name = "статус оспаривания"
        verbose_name_plural = "6.9. [Справочник] Статусы оспаривания"
