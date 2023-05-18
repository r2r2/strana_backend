from django.db import models


class AbstractLog(models.Model):
    """
    Абстрактная модель логов
    """
    created = models.DateTimeField(auto_now=True, verbose_name="Создано")
    state_before = models.JSONField(blank=True, null=True, verbose_name="Состояние до")
    state_after = models.JSONField(blank=True, null=True, verbose_name="Состояние после")
    state_difference = models.JSONField(blank=True, null=True, verbose_name="Разница состояний")
    content = models.TextField(blank=True, null=True, verbose_name="Контент")
    error_data = models.TextField(blank=True, null=True, verbose_name="Данные ошибки")
    response_data = models.TextField(blank=True, null=True, verbose_name="Данные ответа")
    use_case = models.CharField(max_length=200, blank=True, null=True, verbose_name="Сценарий")

    class Meta:
        managed = False
        abstract = True
