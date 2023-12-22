from django.db import models


class MortgageProgram(models.Model):
    """
    Ипотечные программы
    """
    name: str = models.CharField(max_length=255, verbose_name="Название программы")
    priority: int = models.IntegerField(verbose_name="Приоритет", default=0)
    external_code: str = models.TextField(verbose_name="Внешний код")
    slug: str = models.CharField(max_length=255, verbose_name="Слаг")

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = 'mortgage_calculator_program'
        verbose_name = "Ипотечная программа"
        verbose_name_plural = "21.6 Ипотечные программы"
