from django.db import models

from task_management.entities import BaseTaskManagementModel


class TaskChain(BaseTaskManagementModel):
    """
    Цепочка заданий
    """

    name: str = models.CharField(max_length=100, verbose_name='Название')
    sensei_pid: int = models.IntegerField(verbose_name='ID процесса в Sensei', null=True, blank=True)
    booking_substage: models.ManyToManyField = models.ManyToManyField(
        to='booking.AmocrmStatus',
        verbose_name='Статус сделки',
        related_name='taskchain_booking_substages',
        help_text='Первое задание в цепочке будет создано при достижении сделкой данного статуса',
        through='TaskChainStatusThrough',
        through_fields=('task_chain_substage', 'status_substage'),
    )
    task_visibility: models.ManyToManyField = models.ManyToManyField(
        to='booking.AmocrmStatus',
        verbose_name='Видимость заданий',
        related_name='taskchain_task_visibilities',
        help_text='Задание будет видно только в данных статусах, в последующих статусах оно будет не видно',
        through='TaskChainTaskVisibilityStatusThrough',
        through_fields=('task_chain_visibility', 'status_visibility'),
    )
    task_fields: models.ManyToManyField = models.ManyToManyField(
        to='task_management.TaskField',
        verbose_name='Поля задания',
        related_name='taskchains',
        help_text='Поля задания',
        through='TaskChainTaskFieldsThrough',
        through_fields=('task_chain_field', 'task_field'),
        blank=True,
    )
    booking_source: models.ManyToManyField = models.ManyToManyField(
        to='booking.BookingSource',
        verbose_name='Источник бронирования',
        related_name='taskchains',
        help_text='Задачи из данной цепочки будут создаваться у данных типов сделок',
        through='TaskChainBookingSourceThrough',
        through_fields=('task_chain', 'booking_source'),
        blank=True,
    )
    interchangeable_chains: models.ManyToManyField = models.ManyToManyField(
        to='task_management.TaskChain',
        verbose_name='Взаимозаменяемые цепочки',
        related_name='taskchain_interchangeable_chains',
        through='TaskChainInterchangeableThrough',
        through_fields=('task_chain', 'interchangeable_chain'),
        blank=True,
    )
    systems: models.ManyToManyField = models.ManyToManyField(
        to='settings.SystemList',
        verbose_name='Где выводить',
        related_name='taskchains',
        through='TaskChainSystemsThrough',
        through_fields=('task_chain', 'system'),
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = 'task_management_taskchain'
        verbose_name = 'Цепочка заданий'
        verbose_name_plural = '9.1. Цепочки заданий'


class TaskChainStatusThrough(models.Model):
    """
    Связь между цепочкой заданий и статусами сделок
    """
    task_chain_substage: models.ForeignKey = models.OneToOneField(
        to='task_management.TaskChain',
        on_delete=models.CASCADE,
        related_name='task_chain_substage',
        verbose_name='Цепочка заданий',
        primary_key=True,
    )
    status_substage: models.ForeignKey = models.ForeignKey(
        to='booking.AmocrmStatus',
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
    task_chain_visibility: models.ForeignKey = models.OneToOneField(
        to='task_management.TaskChain',
        on_delete=models.CASCADE,
        related_name='task_chain_visibility',
        verbose_name='Цепочка заданий',
        primary_key=True,
    )
    status_visibility: models.ForeignKey = models.ForeignKey(
        to='booking.AmocrmStatus',
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


class TaskChainTaskFieldsThrough(models.Model):
    """
    Связь между цепочкой заданий и полями заданий
    """
    task_chain_field: models.ForeignKey = models.ForeignKey(
        to='task_management.TaskChain',
        on_delete=models.CASCADE,
        related_name='task_chain_field',
        verbose_name='Цепочка заданий',
    )
    task_field: models.ForeignKey = models.ForeignKey(
        to='task_management.TaskField',
        on_delete=models.CASCADE,
        related_name='task_field',
        verbose_name='Поле задания',
        null=True,
    )

    def __str__(self) -> str:
        return f'{self.task_chain_field.name} - {self.task_field.name}'

    class Meta:
        managed = False
        db_table = 'taskchain_taskfields_through'
        verbose_name = 'Связь между цепочкой заданий и полями заданий'
        verbose_name_plural = 'Связи между цепочками заданий и полями заданий'


class TaskChainBookingSourceThrough(models.Model):
    """
    Связь между цепочкой заданий и источниками бронирования
    """
    task_chain: models.ForeignKey = models.ForeignKey(
        to='task_management.TaskChain',
        on_delete=models.CASCADE,
        related_name='task_chain',
        verbose_name='Цепочка заданий',
    )
    booking_source: models.ForeignKey = models.ForeignKey(
        to='booking.BookingSource',
        on_delete=models.CASCADE,
        related_name='booking_source',
        verbose_name='Источник бронирования',
    )

    def __str__(self) -> str:
        return f'{self.task_chain.name} - {self.booking_source.name}'

    class Meta:
        managed = False
        db_table = 'taskchain_booking_source_through'
        verbose_name = 'Связь между цепочкой заданий и источниками бронирования'
        verbose_name_plural = 'Связи между цепочками заданий и источниками бронирования'


class TaskChainInterchangeableThrough(models.Model):
    """
    Связь между цепочкой заданий и взаимозаменяемыми цепочками
    """
    task_chain: models.ForeignKey = models.ForeignKey(
        to='task_management.TaskChain',
        on_delete=models.CASCADE,
        related_name='task_chain_interchangeable_through',
        verbose_name='Цепочка заданий',
    )
    interchangeable_chain: models.ForeignKey = models.ForeignKey(
        to='task_management.TaskChain',
        on_delete=models.CASCADE,
        related_name='interchangeable_chain',
        verbose_name='Взаимозаменяемая цепочка',
    )

    def __str__(self) -> str:
        return f'{self.task_chain.name} - {self.interchangeable_chain.name}'

    class Meta:
        managed = False
        db_table = 'taskchain_interchangeable_through'
        verbose_name = 'Связь между цепочкой заданий и взаимозаменяемыми цепочками'
        verbose_name_plural = 'Связи между цепочками заданий и взаимозаменяемыми цепочками'


class TaskChainSystemsThrough(models.Model):
    """
    Связь между цепочкой заданий и системами
    """
    task_chain: models.ForeignKey = models.ForeignKey(
        to='task_management.TaskChain',
        on_delete=models.CASCADE,
        related_name='task_chain_systems_through',
        verbose_name='Цепочка заданий',
    )
    system: models.ForeignKey = models.ForeignKey(
        to='settings.SystemList',
        on_delete=models.CASCADE,
        related_name='system',
        verbose_name='Система',
    )

    def __str__(self) -> str:
        return f'{self.task_chain.name} - {self.system.name}'

    class Meta:
        managed = False
        db_table = 'taskchain_systems_through'
        verbose_name = 'Связь между цепочкой заданий и системами'
        verbose_name_plural = 'Связи между цепочками заданий и системами'
