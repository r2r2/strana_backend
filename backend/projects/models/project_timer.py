from django.db import models
from request_forms.constants import ProjectTimerRequestType


class ProjectTimer(models.Model):
    """ Модель таймера проекта """


    start = models.DateTimeField(verbose_name="Дата начала", null=True, blank=True)
    news = models.ForeignKey(
        verbose_name="Новость", to="news.News", on_delete=models.SET_NULL, blank=True, null=True
    )
    end = models.DateTimeField(verbose_name="Дата окончания", null=True, blank=True)
    text_button = models.CharField(
        verbose_name="Текст для кнопки", max_length=100, null=True, blank=True
    )
    short_description = models.CharField(verbose_name="Краткое описание", max_length=80, blank=True)
    description = models.TextField(verbose_name="Описание", max_length=100, blank=True)
    request_type = models.CharField(
        verbose_name="Тип формы", blank=True, max_length=32, choices=ProjectTimerRequestType.choices
    )

    def __str__(self):
        return f"Таймер {self.pk}"

    class Meta:
        verbose_name = "Таймер проекта"
        verbose_name_plural = "Таймеры проектов"
