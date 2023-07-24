from django.db import models
from django.utils.translation import gettext_lazy as _

from task_management.entities import BaseTaskManagementModel


class Button(BaseTaskManagementModel):
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
    status: models.ForeignKey = models.ForeignKey(
        'task_management.TaskStatus',
        on_delete=models.CASCADE,
        related_name='button',
        help_text='Статус задания, в котором данное действие будет выводиться',
        verbose_name='Статус',
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.label

    class Meta:
        managed = False
        db_table = 'task_management_button'
        verbose_name = 'Кнопка'
        verbose_name_plural = '9.3. [Справочник] Кнопки (в задачах)'
