from django.db import models
from django.utils.translation import gettext_lazy as _

from task_management.entities import BaseTaskManagementModel


class TaskStatus(BaseTaskManagementModel):
    """
    Статус задачи
    """

    class TaskStatusType(models.TextChoices):
        """
        Тип статуса задачи
        """

        SUCCESS: str = "success", _("Успех")
        ERROR: str = "error", _("Ошибка")
        CHECK: str = "check", _("Проверка")
        START: str = "start", _("Начало")

    name: str = models.CharField(
        max_length=100, verbose_name='Название', help_text='Выводится в списке сущностей и в карточке сущности.'
    )
    description: str = models.TextField(verbose_name='Описание', help_text='Выводится в карточке сущности.')
    slug: str = models.CharField(
        max_length=255,
        verbose_name='Символьный код (слаг)',
        help_text='Слаг определяет статус, '
                  'на который будет происходить переход при выполнении триггера '
                  'согласно бизнес-процесу задания. Все слаги зашиты в код.'
    )
    priority: int = models.IntegerField(
        verbose_name='Приоритет',
        help_text='Чем больше приоритет, тем выше будет выводиться задание в карточке (если заданий несколько)',
    )
    type: str = models.CharField(
        max_length=20,
        verbose_name='Тип',
        help_text='Влияет на выводимую иконку',
        choices=TaskStatusType.choices,
    )
    tasks_chain: models.ForeignKey = models.ForeignKey(
        'task_management.TaskChain',
        on_delete=models.CASCADE,
        related_name='task_statuses',
        help_text='Определяет триггер запуска первого задания в цепочке (задается в цепочке заданий). '
                  'Логика переходов заданий по цепочке зашита в коде.',
        verbose_name='Цепочка заданий [Бизнес-процесс]',
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = 'task_management_taskstatus'
        verbose_name = 'Статус задачи'
        verbose_name_plural = 'Статусы задач'
