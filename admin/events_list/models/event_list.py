from datetime import date

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
    event_id: int = models.IntegerField(
        verbose_name="ID мероприятия",
        null=True,
        blank=True,
    )
    event_date: date = models.DateField(
        verbose_name="Дата и время мероприятия",
        null=True,
        blank=True,
    )
    start_showing_date: date = models.DateField(
        verbose_name="Дата начала показа мероприятия",
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
    text: str = models.TextField(
        verbose_name="Текст в модальном окне",
        null=True,
        blank=True,
        default="QR-код активен 1 раз после прохода, пересылка третьим лицам запрещена",
    )

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        managed = False
        verbose_name = "Список мероприятий"
        verbose_name_plural = "18.1 Список мероприятий"
        db_table = "event_list"
