from django.db import models


class EventParticipantList(models.Model):
    """
    Список участников мероприятия.
    """
    phone: str = models.CharField(
        verbose_name="Номер телефона пользователя",
        max_length=36,
        null=True,
        blank=True,
    )
    event: str = models.ForeignKey(
        verbose_name="Название мероприятия",
        null=True,
        blank=True,
        to='events_list.EventList',
        on_delete=models.SET_NULL,
        related_name="event_participant_list",
    )
    code: str = models.CharField(
        verbose_name="Код для QR кода",
        max_length=255,
        null=True,
        blank=True,
    )
    group_id: int = models.IntegerField(
        verbose_name="ID группы",
        null=True,
        blank=True,
    )
    timeslot: str = models.CharField(
        verbose_name="Время проведения мероприятия",
        max_length=255,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.phone}"

    class Meta:
        managed = False
        verbose_name = "Участник мероприятия"
        verbose_name_plural = "Список участников мероприятия"
        db_table = "event_participant_list"
