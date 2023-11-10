from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


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
        help_text="Локальное время в браузере конвертируется в UTC - нужно учитывать, "
                  "в каком часовом поясе заполняется админка",
    )
    meeting_date_end = models.DateTimeField(
        verbose_name="Дата и время конца мероприятия",
        null=True,
        blank=True,
        help_text="Локальное время в браузере конвертируется в UTC - нужно учитывать, "
                  "в каком часовом поясе заполняется админка",
    )
    record_date_end = models.DateTimeField(
        verbose_name="Дата и время окончания записи на мероприятие",
        null=True,
        blank=True,
        help_text="Дата и время окончания записи на мероприятие - в указанный день возможность записи пропадет, "
                  "если дата не указана - запись пропадет в момент начала мероприятия "
                  "(локальное время в браузере конвертируется в UTC - нужно учитывать, "
                  "в каком часовом поясе заполняется админка)",
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
    time_to_send_sms_before: models.DateTimeField = models.DateTimeField(
        verbose_name='Дата и время отправки смс участникам до начала мероприятия',
        null=True,
        blank=True,
        help_text="Локальное время в браузере конвертируется в UTC - нужно учитывать, "
                  "в каком часовом поясе заполняется админка",
    )
    time_to_send_sms_after: models.DateTimeField = models.DateTimeField(
        verbose_name='Дата и время отправки смс участникам после окончания мероприятия',
        null=True,
        blank=True,
        help_text="Локальное время в браузере конвертируется в UTC - нужно учитывать, "
                  "в каком часовом поясе заполняется админка",
    )

    def __str__(self):
        return self.name

    def clean(self):
        if self.time_to_send_sms_before and self.time_to_send_sms_before > self.meeting_date_start:
            raise ValidationError(
                {"time_to_send_sms_before": "Дата и время отправки смс участникам до начала "
                                            "мероприятия не может быть позже даты начала "
                                            "мероприятия!"}
            )
        if self.time_to_send_sms_after:
            if self.meeting_date_end and self.time_to_send_sms_after < self.meeting_date_end:
                raise ValidationError(
                    {"time_to_send_sms_after": "Дата и время отправки смс участникам после окончания "
                                                "мероприятия не может быть раньше даты окончания "
                                                "мероприятия!"}
                )
            elif self.time_to_send_sms_after < self.meeting_date_start:
                raise ValidationError(
                    {"time_to_send_sms_after": "Дата и время отправки смс участникам после окончания "
                                               "мероприятия не может быть раньше даты начала "
                                               "мероприятия (если нет даты окончания мероприятия)!"}
                )

        if self.meeting_date_end and self.meeting_date_end < self.meeting_date_start:
            raise ValidationError({"meeting_date_end": "Дата окончания не может быть ранее даты начала!"})
        if self.type == EventType.OFFLINE and not self.city:
            raise ValidationError("Для офлайн мероприятия необходимо указать город")
        if self.link:
            url_validator = URLValidator()
            try:
                url_validator(self.link)
            except ValidationError:
                raise ValidationError('Неверный URL-адрес для ссылки на мероприятие.')

    def save(self, *args, **kwargs):
        if not self.record_date_end:
            self.record_date_end = self.meeting_date_start
        super().save()

    class Meta:
        managed = False
        db_table = "event_event"
        verbose_name = "Мероприятие"
        verbose_name_plural = "8.1. Мероприятия"
