from __future__ import unicode_literals
from django.db import models
from .managers import LocationManager


class Location(models.Model):
    """
    Локация
    """

    objects = LocationManager()

    ip_block = models.CharField(verbose_name='Блок IP-адресов',  max_length=64)
    start_ip = models.BigIntegerField(verbose_name='Начальный IP-адрес блока, преобразованный в число', db_index=True)
    end_ip = models.BigIntegerField(verbose_name='Конечный IP-адрес блока, преобразованный в число', db_index=True)
    city = models.CharField(verbose_name='Город', max_length=255, null=True, db_index=True)
    city_id = models.IntegerField(verbose_name='Ipgeobase Id Города', null=True)
    region = models.CharField(verbose_name='Регион', max_length=255, null=True)
    district = models.CharField(verbose_name='Округ', max_length=255, null=True)
    latitude = models.FloatField(verbose_name='Широта', null=True)
    longitude = models.FloatField(verbose_name='Долгота', null=True)
    country = models.CharField(verbose_name='Страна', max_length=16)

    class Meta:
        index_together = [
            ('start_ip', 'end_ip'),
        ]
        unique_together = [
            ('start_ip', 'end_ip'),
        ]

class IPLocation(models.Model):
    """Модель для хранения данных, полученных из Dadata."""
    ip_address = models.GenericIPAddressField(verbose_name='IP адрес')
    city = models.ForeignKey(
        'cities.City', on_delete=models.CASCADE, related_name='ip_addresses',
        verbose_name='город'
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='время создания/изменения записи')

    class Meta:
        verbose_name = 'Данные городов из DaData'
        indexes = [
            models.Index(fields=['ip_address'], name='location_ip_idx')
        ]
