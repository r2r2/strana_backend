from django.db import models
from ..constants import DvizhProgramType

class Program(models.Model):
    """
    Программа ипотеки
    """

    name = models.CharField(verbose_name="Название", max_length=200)
    order = models.PositiveSmallIntegerField(verbose_name="Порядок", default=0, db_index=True)
    dvizh_type = models.CharField(
        verbose_name="Тип предложения для Движ.Api",
        choices=DvizhProgramType.choices,
        default=DvizhProgramType.STANDARD,
        max_length=32
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Программа ипотеки"
        verbose_name_plural = "Программы ипотеки"
        ordering = ("order",)
