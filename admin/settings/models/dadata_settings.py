from django.db import models


class DaDataSettings(models.Model):
    """
    Модель настройки аdторизации в DaData
    """
    api_key: str = models.TextField(verbose_name='API ключ', null=False)
    secret_key = models.TextField(verbose_name='Секрет', null=False)

    class Meta:
        managed = False
        db_table = 'cities_dadata_settings'
        verbose_name = "Настройки подключения Dadata"
        verbose_name_plural = "15.3 - Настройки подключения Dadata"
