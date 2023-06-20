from django.db import models

from task_management.entities import BaseTaskManagementModel


class TaskInstance(BaseTaskManagementModel):
    """
    Задача
    """
    comment: str = models.TextField(
        verbose_name='Комментарий администратора AMO',
        help_text='Текст комментария администратора (из АМО) в случае отказа',
        null=True,
        blank=True
    )
    task_amocrmid: str = models.CharField(max_length=255, verbose_name='AMOCRMID_задания', null=True, blank=True)
    status: models.ForeignKey = models.ForeignKey(
        'task_management.TaskStatus',
        on_delete=models.CASCADE,
        related_name='task_instances',
        verbose_name='Статус задания',
        help_text='Логика переходов заданий между шаблонами зашита и описана в проектной документации.',
    )
    booking: models.ForeignKey = models.ForeignKey(
        'booking.Booking',
        on_delete=models.CASCADE,
        related_name='task_instances',
        verbose_name='Бронирование',
        help_text='ID сущности, в которой будет выводиться задание',
    )

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        managed = False
        db_table = 'task_management_taskinstance'
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
