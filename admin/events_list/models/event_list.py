from datetime import datetime

from django.db import models


class EventList(models.Model):
    """
    Список мероприятий.
    """
    name: str = models.CharField(
        verbose_name="Название мероприятия",
        max_length=255,
        null=True,
        blank=True,
    )
    token: str = models.TextField(
        verbose_name="Токен для импорта мероприятия",
        null=True,
        blank=True,
    )
    event_date: datetime = models.DateTimeField(
        verbose_name="Дата и время мероприятия",
        null=True,
        blank=True,
    )
    title: str = models.CharField(
        verbose_name="Заголовок в модальном окне",
        max_length=255,
        null=True,
        blank=True,
    )
    subtitle: str = models.CharField(
        verbose_name="Подзаголовок в модальном окне",
        max_length=255,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        managed = False
        verbose_name = "Список мероприятий"
        verbose_name_plural = "18.1 Список мероприятий"
        db_table = "event_list"
