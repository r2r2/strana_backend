from django.db import models


class AdditionalServiceCategory(models.Model):
    """
    Категория (вид) услуги
    """

    title: str = models.CharField(max_length=150, null=True, verbose_name="Название")
    priority: int = models.IntegerField(default=0, verbose_name="Приоритет")
    active: bool = models.BooleanField(
        verbose_name="Активность", default=True, help_text="Скрыть/Показать категорию"
    )

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = "additional_services_category"
        verbose_name = "категория"
        verbose_name_plural = "17.3. [Справочник] Категория услуг"
