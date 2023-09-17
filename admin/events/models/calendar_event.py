from django.db import models


class CalendarEventType(models.TextChoices):
    """
    Тип события мероприятия.
    """
    EVENT: tuple[str] = "event", "Мероприятие"
    MEETING: tuple[str] = "meeting", "Встреча"


class CalendarEventFormatType(models.TextChoices):
    """
    Тип формата события календаря.
    """
    ONLINE: tuple[str] = "online", "Онлайн"
    OFFLINE: tuple[str] = "offline", "Офлайн"


class CalendarEvent(models.Model):
    """
    Событие календаря.
    """

    title = models.TextField(
        verbose_name='Описание события календаря',
        null=True,
        blank=True,
    )
    type: str = models.CharField(
        verbose_name="Тип события календаря",
        max_length=10,
        choices=CalendarEventType.choices,
    )
    format_type: str = models.CharField(
        verbose_name="Тип формата события календаря",
        max_length=10,
        choices=CalendarEventFormatType.choices,
    )
    date_start = models.DateTimeField(
        verbose_name="Дата и время начала события календаря",
    )
    date_end = models.DateTimeField(
        verbose_name="Дата и время конца события календаря",
        null=True,
        blank=True,
    )
    event = models.OneToOneField(
        "events.Event",
        models.CASCADE,
        verbose_name="Мероприятие",
        related_name="calendar_event",
        blank=True,
        null=True,
    )
    meeting = models.OneToOneField(
        "events.Meeting",
        models.CASCADE,
        verbose_name="Встреча",
        related_name="calendar_event",
        blank=True,
        null=True,
    )
    tags = models.ManyToManyField(
        verbose_name="Теги события календаря",
        to="events.EventTag",
        through="CalendarEventTagThrough",
        through_fields=("calendar_event", "tag"),
        related_name="calendar_event",
        blank=True,
    )

    def __str__(self):
        return f"#{self.id}"

    def save(self, *args, **kwargs):
        if self.event:
            self.title = self.event.name
            self.type = CalendarEventType.EVENT
            self.format_type = self.event.type
            self.date_start = self.event.meeting_date_start
            self.date_end = self.event.meeting_date_end
        elif self.meeting:
            if self.meeting.type == "kc":
                format_type = "online"
            else:
                format_type = "offline"
            self.type = CalendarEventType.MEETING
            self.format_type = format_type
            self.date_start = self.meeting.date
        super().save()

    class Meta:
        managed = False
        db_table = "event_calendar_event"
        verbose_name = verbose_name_plural = "Событие календаря"


class CalendarEventTagThrough(models.Model):
    calendar_event = models.OneToOneField(
        verbose_name="Событие календаря",
        to="events.CalendarEvent",
        on_delete=models.CASCADE,
        related_name="through_tags",
        primary_key=True,
    )
    tag = models.ForeignKey(
        verbose_name="Тег мероприятия",
        to="events.EventTag",
        on_delete=models.CASCADE,
        related_name="through_calendar_events",
        unique=False,
    )

    class Meta:
        managed = False
        db_table = "event_event_tag_and_calendar_event"
        unique_together = ('calendar_event', 'tag')
        verbose_name = "Событие-Тег"
        verbose_name_plural = "Событие-Теги"


class CalendarEventTypeSettings(models.Model):
    """
    Настройки типов событий календаря.
    """

    type: str = models.CharField(
        unique=True,
        verbose_name="Тип события календаря",
        max_length=10,
        choices=CalendarEventType.choices,
    )
    color = models.CharField(
        verbose_name='Цвет типа события календаря',
        max_length=40,
        default="#808080",
        help_text="HEX код цвета, например #808080",
    )

    def __str__(self):
        return self.color

    class Meta:
        managed = False
        db_table = "event_calendar_event_type_settings"
        verbose_name = "Настройки типов событий календаря"
        verbose_name_plural = "8.4. [Справочник] Настройки типов событий календаря"
