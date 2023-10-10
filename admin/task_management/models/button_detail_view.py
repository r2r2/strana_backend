from django.db import models
from django.utils.translation import gettext_lazy as _

from task_management.entities import BaseTaskManagementModel


class ButtonDetailView(BaseTaskManagementModel):
    """
    Кнопка
    """
    class ButtonStyle(models.TextChoices):
        """
        Стили кнопок
        """
        PRIMARY: str = "primary", _("Основной")
        SECONDARY: str = "secondary", _("Второстепенный")
        DANGER: str = "danger", _("Опасный")
        WARNING: str = "warning", _("Предупреждение")
        INFO: str = "info", _("Информация")
        LIGHT: str = "light", _("Светлый")
        DARK: str = "dark", _("Темный")
        LINK: str = "link", _("Ссылка")

    label: str = models.CharField(max_length=100, verbose_name='Название')
    style: str = models.CharField(
        max_length=20,
        verbose_name='Стиль',
        choices=ButtonStyle.choices,
    )
    slug: str = models.CharField(
        max_length=255, verbose_name='Слаг', help_text='Действие, инициируемое при нажатии на кнопку'
    )
    priority: int = models.IntegerField(
        verbose_name='Приоритет',
        help_text='Чем меньше приоритет - тем выше выводится кнопка в интерфейсе задания',
        null=True,
        blank=True,
    )
    statuses: models.ManyToManyField = models.ManyToManyField(
        'task_management.TaskStatus',
        through='TaskStatusButtonsDetailThrough',
        related_name='button_detail_views',
        help_text='Статусы задания, в которых данное действие будет выводиться',
        verbose_name='Статусы',
        blank=True,
    )

    def __str__(self) -> str:
        return self.label

    class Meta:
        managed = False
        db_table = 'task_management_button_detail_view'
        verbose_name = 'Кнопка'
        verbose_name_plural = '9.6. [Справочник] Кнопки в деталках задач'


class TaskStatusButtonsDetailThrough(models.Model):
    """
    Связь между статусами заданий и кнопками в деталках задач
    """
    task_status: models.OneToOneField = models.OneToOneField(
        to='task_management.TaskStatus',
        on_delete=models.CASCADE,
        related_name='task_status_buttons_detail_through',
        verbose_name='Статус задания',
        primary_key=True,
    )
    button: models.ForeignKey = models.ForeignKey(
        to='task_management.ButtonDetailView',
        on_delete=models.CASCADE,
        related_name='task_status_buttons_detail_through',
        verbose_name='Кнопка',
    )

    class Meta:
        managed = False
        db_table = 'task_management_taskstatus_buttons_detail'
