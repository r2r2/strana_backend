from django.db import models

from task_management.entities import BaseTaskManagementModel


class TaskGroupStatus(BaseTaskManagementModel):
    """
    Группирующие статусы для задач
    """

    name: str = models.CharField(max_length=255, verbose_name='Название')
    priority: int = models.IntegerField(default=0, verbose_name='Приоритет')
    color: str = models.CharField(max_length=16, null=True, blank=True, verbose_name='HEX код цвета')
    slug: str = models.CharField(max_length=255, verbose_name='Слаг группового статуса')

    task_chain: models.ForeignKey = models.ForeignKey(
        to='task_management.TaskChain',
        verbose_name='Цепочка задач',
        related_name='task_group_statuses',
        help_text='Цепочка задач',
        on_delete=models.CASCADE,
    )

    statuses: models.ManyToManyField = models.ManyToManyField(
        to='task_management.TaskStatus',
        verbose_name='Статусы задач',
        related_name='task_group_statuses',
        through='TaskGroupStatusThrough',
        through_fields=('task_group_status', 'task_status'),
        blank=True,
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = 'task_management_group_statuses'
        verbose_name = 'Группирующий статус для задач'
        verbose_name_plural = '9.7. [Справочник] Группирующие статусы задач'


class TaskGroupStatusThrough(models.Model):
    """
    Связь между группирующим статусом и статусом задачи
    """
    task_group_status: models.ForeignKey = models.ForeignKey(
        to='task_management.TaskGroupStatus',
        verbose_name='Группирующий статус',
        related_name='task_group_status_through',
        help_text='Группирующий статус',
        on_delete=models.CASCADE,
    )
    task_status: models.ForeignKey = models.ForeignKey(
        to='task_management.TaskStatus',
        verbose_name='Статус задачи',
        related_name='task_group_status_through',
        help_text='Статус задачи',
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.task_group_status} - {self.task_status}"

    class Meta:
        managed = False
        db_table = 'task_management_group_status_through'
        verbose_name = 'Связь между группирующим статусом и статусом задачи'
        verbose_name_plural = '9.8. Связи между группирующим статусом и статусом задачи'
