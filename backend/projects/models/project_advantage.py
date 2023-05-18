from django.db import models
from ckeditor.fields import RichTextField
from projects.models import Project


class ProjectAdvantage(models.Model):
    """
    Преимущество
    """

    WIDTH = 600
    HEIGHT = 780

    title = models.CharField(verbose_name="Заголовок", max_length=200)
    subtitle = models.CharField(verbose_name="Подзаголовок", max_length=200, blank=True)
    text = RichTextField(verbose_name="Текст", blank=True, max_length=600)

    project = models.ForeignKey(
        verbose_name="Проект", to=Project, on_delete=models.CASCADE, related_name="advantages"
    )
    button_name = models.CharField(
        verbose_name="Название кнопки",
        blank=True,
        max_length=32,
        help_text="Если не заполнено, не выводится. Можно установить ссылку ИЛИ добавить форму обратного звонка.",
    )
    button_link = models.CharField(
        verbose_name="Ссылка кнопки",
        blank=True,
        max_length=200,
        help_text="Укажите относительный путь или абсолютный, вместе с 'Открывать ссылку в новой вкладке'",
    )
    button_link_blank = models.BooleanField(
        verbose_name="Открывать ссылку в новой вкладке", default=False
    )
    button_callback = models.BooleanField(
        verbose_name="Форма обратного звонка на кнопке", default=False
    )

    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)

    class Meta:
        verbose_name = "Преимущество"
        verbose_name_plural = "Преимущества"
        ordering = ("order",)
