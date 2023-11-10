from django.db import models


class QRcodeSMSNotify(models.Model):
    """
    Уведомление о QR-коде для смс.
    """

    sms_template: models.ForeignKey = models.ForeignKey(
        to='notifications.SmsTemplate',
        on_delete=models.CASCADE,
        related_name='qrcode_sms',
        verbose_name='Шаблон cмс',
        null=True,
        blank=True,
    )
    cities: models.ManyToManyField = models.ManyToManyField(
        to='references.Cities',
        related_name='qrcode_sms',
        through='QRcodeSMSCityThrough',
        verbose_name='Города',
        blank=True,
    )
    events: models.ManyToManyField = models.ManyToManyField(
        to='events_list.EventList',
        related_name='qrcode_sms',
        through='QRcodeSMSEventListThrough',
        verbose_name='Мероприятия',
        blank=True,
    )
    time_to_send: models.DateTimeField = models.DateTimeField(
        verbose_name='Дата и время отправки смс',
        null=True,
        blank=True,
        help_text="СМС-уведомление отправляется по местному времени первого города, указанного для отправки уведомления"
    )
    groups: models.ManyToManyField = models.ManyToManyField(
        to='events_list.EventGroup',
        related_name='qrcode_sms',
        through='QRCodeSMSGroupThrough',
        verbose_name='Группы',
        blank=True,
    )

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        managed = False
        db_table = 'notifications_qrcode_sms'
        verbose_name = "Уведомление о QR-коде для смс"
        verbose_name_plural = " 4.9. [Настройки] Отправка SMS по QR-кодам"


class QRcodeSMSCityThrough(models.Model):
    """
    Мероприятия, для которых настроено уведомление о QR-коде для смс.
    """
    qrcode_sms: models.ForeignKey = models.ForeignKey(
        to='notifications.QRcodeSMSNotify',
        related_name='city_through',
        verbose_name='Уведомление о QR-коде для смс',
        on_delete=models.CASCADE,
    )
    city: models.ForeignKey = models.ForeignKey(
        to='references.Cities',
        related_name='qrcode_sms_through',
        verbose_name='Город',
        on_delete=models.CASCADE,
    )

    class Meta:
        managed = False
        db_table = 'notifications_qrcode_sms_city_through'
        verbose_name = "Проекты, для которых настроено уведомление о QR-коде для смс"
        verbose_name_plural = "Проекты, для которых настроено уведомление о QR-коде для смс"


class QRcodeSMSEventListThrough(models.Model):
    """
    Мероприятия, для которых настроено уведомление о QR-коде для смс.
    """
    qrcode_sms: models.ForeignKey = models.ForeignKey(
        to='notifications.QRcodeSMSNotify',
        related_name='eventlist_through',
        verbose_name='Уведомление о QR-коде для смс',
        on_delete=models.CASCADE,
    )
    event: models.ForeignKey = models.ForeignKey(
        to='events_list.EventList',
        related_name='qrcode_sms_through',
        verbose_name='Мероприятие',
        on_delete=models.CASCADE,
    )

    class Meta:
        managed = False
        db_table = 'notifications_qrcode_sms_eventlist_through'
        verbose_name = "Мероприятия, для которых настроено уведомление о QR-коде для смс"
        verbose_name_plural = "Мероприятия, для которых настроено уведомление о QR-коде для смс"


class QRCodeSMSGroupThrough(models.Model):
    """
    Группы, для которых настроено уведомление о QR-коде для смс.
    """
    qrcode_sms: models.ForeignKey = models.ForeignKey(
        to='notifications.QRcodeSMSNotify',
        related_name='group_through',
        verbose_name='Уведомление о QR-коде для смс',
        on_delete=models.CASCADE,
    )
    event_group: models.ForeignKey = models.ForeignKey(
        to='events_list.EventGroup',
        related_name='qrcode_sms_through',
        verbose_name='Группа',
        on_delete=models.CASCADE,
    )

    class Meta:
        managed = False
        db_table = 'notifications_qrcode_sms_eventgroup_through'
        verbose_name = "Группы, для которых настроено уведомление о QR-коде для смс"
        verbose_name_plural = "Группы, для которых настроено уведомление о QR-коде для смс"
