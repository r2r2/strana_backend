from django.db import models


class AdditionalServiceType(models.Model):
    """
    Тип категорий (видов) услуг
    """

    title: str = models.CharField(max_length=150, verbose_name="Название")

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = "additional_services_service_type"
        verbose_name = "тип категории"
        verbose_name_plural = "Типы категорий"
