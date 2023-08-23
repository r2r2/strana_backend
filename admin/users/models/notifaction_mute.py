from django.db import models


class UserNotificationMute(models.Model):
    """
    Условия проверки на уникальность
    """
    times = models.IntegerField(verbose_name="Количество запросов")
    phone = models.CharField(verbose_name="Номер телефона", max_length=20)
    blocked = models.BooleanField(verbose_name="Заблокирован", default=False)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users_notification_mute"
        verbose_name = "Блокировка пользователя"
        verbose_name_plural = " 2.4. [Справочник] Блокировки IP адресов пользователей"


class RealIpUsers(models.Model):
    """
    Условия проверки на уникальность
    """
    times = models.IntegerField(verbose_name="Количество запросов")
    real_ip = models.CharField(verbose_name="IP адрес клиента", max_length=20)
    blocked = models.BooleanField(verbose_name="Заблокирован", default=False)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users_real_ip"
        verbose_name = "IP адрес клиента"
        verbose_name_plural = " 2.3. [Справочник] IP адреса пользователей"
