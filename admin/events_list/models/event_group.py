from django.db import models


class EventGroup(models.Model):
    """
    Группы мероприятий.
    """
    group_id: int = models.IntegerField(
        verbose_name="ID группы",
        null=True,
        blank=True,
    )
    timeslot: str = models.CharField(
        verbose_name="Время проведения мероприятия",
        max_length=24,
        null=True,
        blank=True,
    )
    event: models.ForeignKey = models.ForeignKey(
        to='events_list.EventList',
        related_name='groups',
        verbose_name='Мероприятие',
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"#{self.group_id} {self.event.name} {self.timeslot}"

    class Meta:
        managed = False
        db_table = 'event_groups'
        verbose_name = "Группы мероприятий"
        verbose_name_plural = "18.2 ID группы"
