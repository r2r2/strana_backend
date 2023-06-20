from django.db import models

from task_management.entities import BaseTaskManagementModel


class TaskChain(BaseTaskManagementModel):
    """
    Цепочка заданий
    """

    name: str = models.CharField(max_length=100, verbose_name='Название')
    sensei_pid: int = models.IntegerField(verbose_name='ID процесса в Sensei', null=True, blank=True)
    booking_substage: models.ManyToManyField = models.ManyToManyField(
        to='amocrm.AmocrmStatus',
        verbose_name='Статус сделки',
        related_name='taskchain_booking_substages',
        help_text='Первое задание в цепочке будет создано при достижении сделкой данного статуса',
        through='TaskChainStatusThrough',
        through_fields=('task_chain_substage', 'status_substage'),
    )
    task_visibility: models.ManyToManyField = models.ManyToManyField(
        to='amocrm.AmocrmStatus',
        verbose_name='Видимость заданий',
        related_name='taskchain_task_visibilities',
        help_text='Задание будет видно только в данных статусах, в последующих статусах оно будет не видно',
        through='TaskChainTaskVisibilityStatusThrough',
        through_fields=('task_chain_visibility', 'status_visibility'),
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = 'task_management_taskchain'
        verbose_name = 'Цепочка заданий'
        verbose_name_plural = 'Цепочки заданий'


class TaskChainStatusThrough(models.Model):
    """
    Связь между цепочкой заданий и статусами сделок
    """
    task_chain_substage: models.ForeignKey = models.ForeignKey(
        to='task_management.TaskChain',
        on_delete=models.CASCADE,
        related_name='task_chain_substage',
        verbose_name='Цепочка заданий',
        primary_key=True,
    )
    status_substage: models.ForeignKey = models.ForeignKey(
        to='amocrm.AmocrmStatus',
        on_delete=models.CASCADE,
        related_name='status_substage',
        verbose_name='Статус сделки',
    )

    def __str__(self) -> str:
        return f'{self.task_chain_substage.name} - {self.status_substage.name}'

    class Meta:
        managed = False
        db_table = 'taskchain_status_through'
        verbose_name = 'Связь между цепочкой заданий и статусами сделок'
        verbose_name_plural = 'Связи между цепочками заданий и статусами сделок'


class TaskChainTaskVisibilityStatusThrough(models.Model):
    """
    Связь между цепочкой заданий и статусами сделок, в которых задание будет видно
    """
    task_chain_visibility: models.ForeignKey = models.ForeignKey(
        to='task_management.TaskChain',
        on_delete=models.CASCADE,
        related_name='task_chain_visibility',
        verbose_name='Цепочка заданий',
        primary_key=True,
    )
    status_visibility: models.ForeignKey = models.ForeignKey(
        to='amocrm.AmocrmStatus',
        on_delete=models.CASCADE,
        related_name='status_visibility',
        verbose_name='Статус сделки',
    )

    def __str__(self) -> str:
        return f'{self.task_chain_visibility.name} - {self.status_visibility.name}'

    class Meta:
        managed = False
        db_table = 'taskchain_taskvisibility_status_through'
        verbose_name = 'Связь между цепочкой заданий и статусами сделок, в которых задание будет видно'
        verbose_name_plural = 'Связи между цепочками заданий и статусами сделок, в которых задание будет видно'
