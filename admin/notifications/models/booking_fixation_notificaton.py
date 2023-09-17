from django.db import models
from django.utils.translation import gettext_lazy as _


class BookingFixationNotification(models.Model):
    """
    Уведомление при окончании фиксации.
    """
    class BookingFixationNotificationTypeChoices(models.TextChoices):
        EXTEND = "extend", _("Продление фиксации")
        FINISH = "finish", _("Окончание фиксации")

    mail_template: models.ForeignKey = models.ForeignKey(
        to='notifications.EmailTemplate',
        on_delete=models.CASCADE,
        related_name='booking_fixation_notifications',
        verbose_name='Шаблон письма',
        null=True,
        blank=True,
    )
    type: models.CharField = models.CharField(
        choices=BookingFixationNotificationTypeChoices.choices,
        verbose_name='Тип события',
        null=True,
        max_length=100,
        blank=True,
    )
    project: models.ManyToManyField = models.ManyToManyField(
        to='properties.Project',
        related_name='booking_fixation_notifications',
        through='BookingFixationNotificationsProjectThrough',
        verbose_name='Проект (ЖК)',
        blank=True,
    )
    days_before_send: models.FloatField = models.FloatField(
        verbose_name='За сколько дней до события отправлять',
        null=True,
        blank=True,
    )

    class Meta:
        managed = False
        db_table = 'booking_fixation_notifications'
        verbose_name = 'Уведомление при окончании фиксации'
        verbose_name_plural = '4.7. [Настройки] Напоминания о фиксировании'


class BookingFixationNotificationsProjectThrough(models.Model):
    """
    Проекты, для которых настроено уведомление при окончании фиксации.
    """
    booking_fixation_notification: models.ForeignKey = models.ForeignKey(
        to='BookingFixationNotification',
        on_delete=models.CASCADE,
        related_name='project_through',
        verbose_name='Уведомление при окончании фиксации',
    )
    project: models.ForeignKey = models.ForeignKey(
        to='properties.Project',
        on_delete=models.CASCADE,
        related_name='booking_fixation_notification_through',
        verbose_name='Проект (ЖК)',
    )

    class Meta:
        managed = False
        db_table = 'booking_fixation_notifications_project_through'
        verbose_name = 'Проекты, для которых настроено уведомление при окончании фиксации'
        verbose_name_plural = '[Связь] Проекты, для которых настроено уведомление при окончании фиксации'
