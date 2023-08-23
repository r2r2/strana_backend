from django.db import models

from task_management.entities import BaseTaskManagementModel


class TaskInstance(BaseTaskManagementModel):
    """
    Задача
    """
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
    task_amocrmid: str = models.CharField(
        max_length=255,
        verbose_name='AMOCRMID_задания',
        null=True,
        blank=True,
        help_text="ID связанного процесса Sensei, по данному полю производится сопоставление запускаемого процесса в "
                  "AMOCRM",
    )
    comment: str = models.TextField(
        verbose_name='Комментарий администратора AMO',
        help_text='[Загрузить документы] Текст комментария администратора (из АМО) '
                  'в случае отправки документов на доработку',
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        managed = False
        db_table = 'task_management_taskinstance'
        verbose_name = 'Задача'
        verbose_name_plural = '9.2. Задачи'
