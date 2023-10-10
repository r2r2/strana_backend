from django.db import models
from django.utils.translation import gettext_lazy as _


class EventsSmsNotificationType(models.TextChoices):
    """
    Типы смс уведомлений для брокеров, участвующих в мероприятиях.
    """

    BEFORE = "before", _("До мероприятия")
    AFTER = "after", _("После окончания мероприятия")


class EventsSmsNotification(models.Model):
    """
    Настройки уведомление для брокеров, участвующих в мероприятиях.
    """

    sms_template: models.ForeignKey = models.ForeignKey(
        to='notifications.SmsTemplate',
        on_delete=models.CASCADE,
        related_name='event_sms_notifications',
        verbose_name='Шаблон cмс',
        null=True,
        blank=True,
    )
    sms_event_type: models.CharField = models.CharField(
        choices=EventsSmsNotificationType.choices,
        verbose_name='Тип события отправки смс',
        max_length=100,
        null=True,
        blank=True,
    )
    cities: models.ManyToManyField = models.ManyToManyField(
        to='references.Cities',
        related_name='event_sms_notifications',
        through='EventsSmsNotificationCityThrough',
        verbose_name='Города',
        blank=True,
    )
    days: models.FloatField = models.FloatField(
        verbose_name='За сколько дней до / за сколько дней после события отправлять',
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        managed = False
        db_table = 'notifications_event_sms_notification'
        verbose_name = 'Настройки уведомлений для брокеров, участвующих в мероприятиях'
        verbose_name_plural = '4.8. [Настройки] Отправка SMS по событию календаря (ERD)'


class EventsSmsNotificationCityThrough(models.Model):
    """
    Проекты, для которых настроено уведомление для брокеров, участвующих в мероприятиях.
    """

    event_sms_notification: models.ForeignKey = models.ForeignKey(
        to='EventsSmsNotification',
        on_delete=models.CASCADE,
        related_name='city_through',
        verbose_name='Настройка уведомлений для брокеров, участвующих в мероприятиях',
    )
    city: models.ForeignKey = models.ForeignKey(
        to='references.Cities',
        on_delete=models.CASCADE,
        related_name='event_sms_notification_through',
        verbose_name='Город',
    )

    class Meta:
        managed = False
        db_table = 'notifications_event_sms_notifications_city_through'
        verbose_name = verbose_name_plural = '''Проекты, для которых настроено уведомление для брокеров,
                                             участвующих в мероприятиях'''
