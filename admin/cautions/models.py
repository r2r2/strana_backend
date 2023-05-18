# pylint: disable=no-member,invalid-str-returned
from django.db import models
from django.utils.translation import gettext_lazy as _


class Caution(models.Model):
    """
    Модель предупреждения, выводимого пользователю
    """

    # TODO : предлагаю вынести CautionType из кабинета constants.py
    class CautionType(models.TextChoices):
        """
        Тип предупреждения
        """
        INFORMATION = "information", _("Информация")
        WARNING = "warning", _("Предупреждение")

    is_active = models.BooleanField(verbose_name="Активность", default=False)
    type = models.CharField(
        choices=CautionType.choices,
        default=CautionType.INFORMATION,
        max_length=20,
        verbose_name='Тип'
    )
    roles = models.JSONField(
        null=True,
        blank=True,
        default=list,
        verbose_name="Доступно ролям",
        help_text="Предупреждение будет выводиться всем пользователям с указанными ролями"
    )
    text = models.TextField(verbose_name="Выводимый текст", help_text="HTML-теги недопустимы")
    priority = models.SmallIntegerField(verbose_name="Приоритет", help_text="Приоритет предупреждения")
    expires_at = models.DateTimeField(verbose_name="Активен до", help_text="Когда будет деактивировано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано", help_text="Дата создания")
    updated_at = models.DateTimeField(
        null=True,
        blank=True,
        auto_now=True,
        verbose_name="Обновлено",
        help_text="Дата последнего обновления"
    )
    created_by = models.ForeignKey(
        "users.CabinetUser",
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="cautions_created",
        verbose_name="Кем создано",
        help_text="Кем создано"
    )
    update_by = models.ForeignKey(
        "users.CabinetUser",
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="cautions_updated",
        verbose_name="Кем обновлено",
        help_text="Кем обновлено"
    )

    def __str__(self) -> str:
        if self.type:
            type_value = str(self.CautionType._value2label_map_.get(self.type))
            return type_value
        return self.type

    class Meta:
        managed = False
        db_table = "cautions_caution"
        verbose_name = "Предупреждение"
        verbose_name_plural = "Предупреждения"
        ordering = ["priority"]


class CautionMute(models.Model):
    """
    Модель связи тех, кого уже уведомили предупреждением
    """

    user = models.ForeignKey(
        "users.CabinetUser",
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Пользователь"
    )
    caution = models.ForeignKey(
        "cautions.Caution",
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Предупреждение"
    )

    class Meta:
        managed = False
        db_table = "users_caution_mute"
        verbose_name = "Уведомление пользователя"
        verbose_name_plural = "Уведомления пользователей"
