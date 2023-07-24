from django.db import models
from django.core.exceptions import ValidationError


class EventType(models.TextChoices):
    """
    Тип мероприятия.
    """
    ONLINE: tuple[str] = "online", "Онлайн"
    OFFLINE: tuple[str] = "offline", "Офлайн"


class Event(models.Model):
    """
    Мероприятие.
    """

    name = models.CharField(verbose_name='Название мероприятия', max_length=100)
    description = models.TextField(
        verbose_name='Описание мероприятия',
        null=True,
        blank=True,
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        null=True,
        blank=True,
    )
    type: str = models.CharField(
        verbose_name="Тип мероприятия",
        max_length=10,
        choices=EventType.choices,
    )
    city: models.ForeignKey = models.ForeignKey(
        to='references.Cities',
        related_name='events',
        on_delete=models.CASCADE,
        verbose_name='Город',
        blank=True,
        null=True,
        help_text="Только для офлайн мероприятий",
    )
    address: str = models.TextField(
        verbose_name="Адрес мероприятия (офлайн)",
        null=True,
        blank=True,
        help_text="Только для офлайн мероприятий",
    )
    link: str = models.TextField(
        verbose_name="Ссылка на мероприятие (онлайн)",
        null=True,
        blank=True,
        help_text="Только для онлайн мероприятий",
    )
    meeting_date_start = models.DateTimeField(
        verbose_name="Дата и время начала мероприятия",
    )
    meeting_date_end = models.DateTimeField(
        verbose_name="Дата и время конца мероприятия",
        null=True,
        blank=True,
    )
    record_date_end = models.DateTimeField(
        verbose_name="Дата и время окончания записи на мероприятие",
        null=True,
        blank=True,
        help_text="В указанное время возможность записи пропадет, если дата не указывается, то автоматически "
                  "устанавливается дата начала мероприятия",
    )
    manager_fio: str = models.TextField(
        verbose_name="ФИО ответственного менеджера",
    )
    manager_phone = models.CharField(verbose_name="Номер телефона ответственного менеджера", max_length=20)
    max_participants_number = models.IntegerField(
        verbose_name="Макс. количество участников мероприятия",
        default=0,
        help_text="Максимальное количество мест для записи, вручную вы можете добавить дополнительных участников",
    )
    image: str = models.FileField(
        verbose_name="Картинка мероприятия",
        max_length=500,
        upload_to="d/d/p",
        blank=True,
        null=True,
    )
    show_in_all_cities: bool = models.BooleanField(
        verbose_name="Показывать во всех городах",
        default=True,
        help_text="Только для офлайн мероприятий",
    )
    is_active: bool = models.BooleanField(
        verbose_name="Мероприятие активно",
        default=True,
        help_text="Неактивные мероприятия не показываются в календаре",
    )
    tags = models.ManyToManyField(
        verbose_name="Теги мероприятий",
        to="events.EventTag",
        through="EventTagThrough",
        through_fields=("event", "tag"),
        related_name="events",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    def clean(self):
        if self.meeting_date_end and self.meeting_date_end < self.meeting_date_start:
            raise ValidationError({"meeting_date_end": "Дата окончания не может быть ранее даты начала!"})

    def save(self, *args, **kwargs):
        if not self.record_date_end:
            self.record_date_end = self.meeting_date_start
        super().save()

    class Meta:
        managed = False
        db_table = "event_event"
        verbose_name = "Мероприятие"
        verbose_name_plural = "8.1. Мероприятия"


class EventTagThrough(models.Model):
    event = models.ForeignKey(
        verbose_name="Мероприятие",
        to="events.Event",
        on_delete=models.CASCADE,
        related_name="through_tags",
        primary_key=True,
    )
    tag = models.ForeignKey(
        verbose_name="Тег мероприятия",
        to="events.EventTag",
        on_delete=models.CASCADE,
        related_name="through_events",
        unique=False,
    )

    class Meta:
        managed = False
        db_table = "event_event_tag_and_event"
        unique_together = ('event', 'tag')
        verbose_name = "Мероприятие-Тег"
        verbose_name_plural = "Мероприятия-Теги"
