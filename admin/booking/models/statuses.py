from django.db import models

from .pipelines import AmocrmPipeline
from .group_statuses import AmocrmGroupStatus


class AmocrmStatus(models.Model):
    """
    Таблица статусов из AmoCRM
    """

    id = models.IntegerField(verbose_name='ID статуса из AmoCRM', primary_key=True)
    name = models.CharField(verbose_name='Название статуса', max_length=150)
    sort = models.IntegerField(verbose_name='Сортировка', default=0)
    pipeline = models.ForeignKey(
        AmocrmPipeline, on_delete=models.CASCADE, related_name='statuses', verbose_name="ID воронки из AmoCRM"
    )

    group_status = models.ForeignKey(
        AmocrmGroupStatus,
        on_delete=models.SET_NULL,
        related_name='statuses',
        verbose_name="Группирующий статус",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.pipeline.name} ({self.name})"

    class Meta:
        managed = False
        db_table = "amocrm_statuses"
        ordering = ("pipeline_id", "sort")
        verbose_name = "Статус"
        verbose_name_plural = "1.4. [Справочник] Статусы из АМО"

