from django.db import models
from django.utils.translation import gettext_lazy as _


class IconType(models.TextChoices):
    """
    Тип иконки
    """
    ICON = "icon", _("Иконка")
    IMAGE = "image", _("Изображение")


class StyleListType(models.TextChoices):
    """
    Стиль в списке
    """
    DEFAULT = "default", _("По умолчанию")
    SUCCESS = "success", _("Успешно")
    DANGER = "danger", _("Опасно")
    WARNING = "warning", _("Предупреждение")
    INFO = "info", _("Информация")
    PRIMARY = "primary", _("Первичный")
    SECONDARY = "secondary", _("Вторичный")
    LIGHT = "light", _("Светлый")
    DARK = "dark", _("Темный")
    WHITE = "white", _("Белый")
    TRANSPARENT = "transparent", _("Прозрачный")


class StatusType(models.TextChoices):
    """
    Тип статуса
    """
    PINNING = "pinning", _("Статус закрепления")
    UNIQUE = "unique", _("Статус уникальности")


class UniqueStatus(models.Model):
    """
    Таблица статусов уникальности
    """
    title = models.CharField(
        verbose_name="Заголовок",
        max_length=255,
        help_text="Выделено жирным на странице проверки",
    )
    subtitle = models.CharField(
        verbose_name="Подзаголовок",
        max_length=255,
        null=True,
        blank=True,
        help_text="Выводится под заголовком на странице проверки",
    )
    icon = models.CharField(
        verbose_name="Иконка",
        max_length=36,
        choices=IconType.choices,
    )
    color = models.CharField(
        verbose_name="Цвет текста",
        max_length=7,
        null=True,
        blank=True,
        default="#8F00FF",
        help_text="HEX код цвета названия статуса на странице проверки, по умолчанию - фиолетовый",
    )
    background_color = models.CharField(
        verbose_name="Цвет фона",
        max_length=7,
        null=True,
        blank=True,
        default="#8F00FF",
        help_text="HEX код цвета подложки под иконкой на странице проверки,  по умолчанию - фиолетовый",
    )
    border_color = models.CharField(
        verbose_name="Цвет рамки",
        max_length=7,
        null=True,
        blank=True,
        default="#8F00FF",
        help_text="HEX код цвета рамки иконки на странице проверки,  по умолчанию - фиолетовый",
    )
    slug = models.CharField(verbose_name="Слаг", max_length=255, null=True, blank=True)
    style_list = models.CharField(
        verbose_name="Стиль в списке",
        max_length=36,
        choices=StyleListType.choices,
        null=True,
        blank=True,
        help_text="Стиль статуса, который будет выводиться на странице списка клиентов",
    )
    type = models.CharField(
        verbose_name="Тип",
        max_length=36,
        choices=StatusType.choices,
        null=True,
        blank=True,
        help_text="Используется для сбора значений фильтра по статусу закрепления.",
    )
    comment = models.TextField(
        verbose_name="Комментарий",
        null=True,
        blank=True,
        help_text="Внутренний комментарий по назначению статуса",
    )
    can_dispute = models.BooleanField(
        verbose_name="Можно оспорить статус клиента",
        default=False,
    )

    class Meta:
        managed = False
        db_table = "users_unique_statuses"
        verbose_name = "Статус уникальности"
        verbose_name_plural = "6.2. Условия определения статуса уникальности"

    def __str__(self):
        return self.title
