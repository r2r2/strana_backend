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
    status: str = models.CharField(
        verbose_name="Статус",
        max_length=20,
        choices=MeetingStatus.choices,
        default=MeetingStatus.START,
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
        return str(self.topic)

    class Meta:
        managed = False
        db_table = 'meetings_meeting'
        verbose_name = "Встреча"
        verbose_name_plural = "13.1. Встречи"