from django.db import models


class AdditionalServiceConditionStep(models.Model):
    """
    Шаг для "Как получить услугу"
    """

    description: str = models.TextField(verbose_name="Текст описания")
    active: bool = models.BooleanField(
        verbose_name="Активность", default=True, help_text="Скрыть/Показать шаг"
    )
    condition: models.ForeignKey = models.ForeignKey(
        to="additional_services.AdditionalServiceCondition",
        related_name="condition_step",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Как получить услуги",
    )
    priority: int = models.IntegerField(default=0, verbose_name="Сортировка")

    def __str__(self):
        return self.description

    class Meta:
        managed = False
        db_table = "additional_services_condition_step"
        verbose_name = "шаг"
        verbose_name_plural = "17.5. [Справочник] Шаг получения сделки"
        ordering = ["priority"]
