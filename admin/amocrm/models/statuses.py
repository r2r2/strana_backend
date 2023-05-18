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
    color = models.CharField(verbose_name='Цвет', max_length=40, blank=True, null=True)
    pipeline = models.ForeignKey(
        AmocrmPipeline, on_delete=models.CASCADE, related_name='statuses', verbose_name="ID воронки из AmoCRM"
    )
    actions = models.ManyToManyField(
        null=True, blank=True,
        verbose_name="Действия по сделкам",
        to="amocrm.AmocrmAction",
        through="StatusActionThrough",
        through_fields=("status", "action"),
        related_name="actions"
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
        verbose_name_plural = "Статусы"


class StatusActionThrough(models.Model):
    status = models.ForeignKey(
        verbose_name="Статус",
        to="amocrm.AmocrmStatus",
        on_delete=models.CASCADE,
        related_name="status",
        primary_key=True
    )
    action = models.ForeignKey(
        verbose_name="Действие",
        to="amocrm.AmocrmAction",
        on_delete=models.CASCADE,
        unique=False,
        related_name="action"
    )

    class Meta:
        managed = False
        db_table = "amocrm_actions_statuses"
        unique_together = ('status', 'action')
        verbose_name = "Статус-Действие"
        verbose_name_plural = "Статусы-Действия"

    def __str__(self):
        return f"{self.status} {self.action}"
