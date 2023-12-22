from django.db import models


class MortgageForm(models.Model):
    """
    Форма ипотечного калькулятора.
    """
    phone: str = models.CharField(
        max_length=20, verbose_name="Номер телефона"
    )
    surname: str = models.CharField(
        max_length=100, verbose_name="Фамилия"
    )
    name: str = models.CharField(
        max_length=100, verbose_name="Имя"
    )
    patronymic: str = models.CharField(
        max_length=100, verbose_name="Отчество"
    )

    def __str__(self) -> str:
        return f"{self.surname} {self.name} {self.patronymic}".strip()

    class Meta:
        managed = False
        db_table = 'mortgage_form'
        verbose_name = "Форма ипотечного калькулятора"
        verbose_name_plural = "21.8 Персональные данные"
