from django.db import models
from django.utils.translation import gettext_lazy as _


class Meeting(models.Model):
    """
    Встреча
    """

    class MeetingStatus(models.TextChoices):
        """
        Статус встречи
        """
        CONFIRM: str = "confirm", _("Подтверждена")
        NOT_CONFIRM: str = "not_confirm", _("Не подтверждена")
        START: str = "start", _("Встреча началась")
        FINISH: str = "finish", _("Завершена")

    class MeetingTopicType(models.TextChoices):
        """
        Тема встречи
        """
        BUY: str = "buy", _("Покупка квартиры")
        MORTGAGE: str = "mortgage", _("Ипотека")

    class MeetingType(models.TextChoices):
        """
        Тип встречи
        """
        ONLINE: str = "kc", _("Онлайн")
        OFFLINE: str = "meet", _("Офлайн")

    class MeetingPropertyType(models.TextChoices):
        """
        Тип помещения
        """
        FLAT: str = "flat", _("Квартира")
        PARKING: str = "parking", _("Паркинг")
        PANTRY: str = "pantry", _("Кладовая")
        COMMERCIAL: str = "commercial", _("Коммерция")
        APARTMENT: str = "apartment", _("Апартаменты")

    city: models.ForeignKey = models.ForeignKey(
        to='references.Cities',
        related_name='meeting_city',
        on_delete=models.CASCADE,
        verbose_name='Город',
        blank=True,
        null=True,
    )
    project: models.ForeignKey = models.ForeignKey(
        to='properties.Project',
        related_name='meeting_project',
        on_delete=models.CASCADE,
        verbose_name='Проект',
        blank=True,
        null=True,
    )
    booking: models.ForeignKey = models.ForeignKey(
        to='booking.Booking',
        related_name='meeting_booking',
        on_delete=models.CASCADE,
        verbose_name='Бронирование',
        blank=True,
        null=True,
    )
    status: models.ForeignKey = models.ForeignKey(
        to='events.MeetingStatus',
        related_name='meetings',
        on_delete=models.SET_NULL,
        verbose_name='Статус встречи deprecated',
        blank=True,
        null=True,
    )
    status_ref: models.ForeignKey = models.ForeignKey(
        to='events.MeetingStatusRef',
        related_name='meetings',
        on_delete=models.SET_NULL,
        verbose_name='Статус встречи',
        blank=True,
        null=True,
    )

    # deprecates
    creation_source: models.ForeignKey = models.ForeignKey(
        to='events.MeetingCreationSource',
        related_name='meetings',
        on_delete=models.SET_NULL,
        verbose_name='Источник создания встречи deprecated',
        blank=True,
        null=True,
    )

    creation_source_ref: models.ForeignKey = models.ForeignKey(
        to='events.MeetingCreationSourceRef',
        related_name='meetings',
        on_delete=models.SET_NULL,
        verbose_name='Источник создания встречи',
        blank=True,
        null=True,
    )

    record_link: str = models.CharField(verbose_name="Ссылка на запись", max_length=255, blank=True, null=True)
    meeting_link: str = models.CharField(verbose_name="Ссылка на встречу", max_length=255, blank=True, null=True)
    meeting_address: str = models.CharField(verbose_name="Адрес встречи", max_length=255, blank=True, null=True)
    topic: str = models.CharField(
        verbose_name="Тема встречи",
        max_length=20,
        choices=MeetingTopicType.choices,
        default=MeetingTopicType.BUY,
    )
    type: str = models.CharField(
        verbose_name="Тип встречи",
        max_length=20,
        choices=MeetingType.choices,
        default=MeetingType.ONLINE,
    )
    property_type: str = models.CharField(
        verbose_name="Тип помещения",
        max_length=20,
        choices=MeetingPropertyType.choices,
        default=MeetingPropertyType.FLAT,
    )
    date: models.DateTimeField = models.DateTimeField(verbose_name="Дата встречи")

    def __str__(self) -> str:
        return f"Встреча #{self.id}"

    class Meta:
        managed = False
        db_table = 'meetings_meeting'
        verbose_name = "Встреча"
        verbose_name_plural = "8.2. Встречи"
