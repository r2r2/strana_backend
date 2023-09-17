from django.db import models


class AdditionalServiceCondition(models.Model):
    """
    Модель "Как получить услугу"
    """

    title: str = models.CharField(max_length=150, null=True, verbose_name="Название")

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = "additional_services_condition"
        verbose_name = "Как получить услугу"
        verbose_name_plural = "17.4. [Справочник] Как получить услугу"
