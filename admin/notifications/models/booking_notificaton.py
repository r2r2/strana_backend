from django.db import models
from django.utils.translation import gettext_lazy as _


class BookingNotification(models.Model):
    """
    Уведомление при платном бронировании
    """
    class CreatedSourceChoices(models.TextChoices):
        AMOCRM = "amocrm", _("AMOCRM")
        LK = "lk_booking", _("Бронирование через личный кабинет")
        FAST_BOOKING = "fast_booking", _("Быстрое бронирование")
        LK_ASSIGN = "lk_booking_assign", _("Закреплен в ЛК Брокера")

    sms_template: models.ForeignKey = models.ForeignKey(
        to='notifications.SmsTemplate',
        on_delete=models.CASCADE,
        related_name='booking_notifications',
        verbose_name='Шаблон смс уведомления',
        null=True,
        blank=True,
    )
    created_source: models.CharField = models.CharField(
        choices=CreatedSourceChoices.choices,
        verbose_name='Источник создания онлайн-бронирования',
        null=True,
        max_length=100,
        blank=True,
    )
    project: models.ManyToManyField = models.ManyToManyField(
        to='properties.Project',
        related_name='booking_notifications',
        through='BookingNotificationsProjectThrough',
        verbose_name='Проект (ЖК)',
        blank=True,
    )
    hours_before_send: models.FloatField = models.FloatField(
        verbose_name='За сколько часов до момента окончания резервирования отправлять (ч)',
        null=True,
        blank=True,
    )

    class Meta:
        managed = False
        db_table = 'booking_notifications'
        verbose_name = 'Уведомление при платном бронировании'
        verbose_name_plural = '4.6. [Настройки] Напоминания о резервированиях'


class BookingNotificationsProjectThrough(models.Model):
    """
    Проекты, для которых настроено уведомление при платном бронировании
    """
    booking_notification: models.ForeignKey = models.ForeignKey(
        to='BookingNotification',
        on_delete=models.CASCADE,
        related_name='project_through',
        verbose_name='Уведомление при платном бронировании',
    )
    project: models.ForeignKey = models.ForeignKey(
        to='properties.Project',
        on_delete=models.CASCADE,
        related_name='booking_notification_through',
        verbose_name='Проект (ЖК)',
    )

    class Meta:
        managed = False
        db_table = 'booking_notifications_project_through'
        verbose_name = 'Проекты, для которых настроено уведомление при платном бронировании'
        verbose_name_plural = '[Связь] Проекты, для которых настроено уведомление при платном бронировании'
