from django.db import models


class MortgageConditionMatrix(models.Model):
    """
    Матрица условий
    """
    name: str = models.CharField(verbose_name="Название", max_length=100)
    amocrm_statuses: models.ManyToManyField = models.ManyToManyField(
        verbose_name="Статусы сделки",
        to="booking.AmocrmStatus",
        through="mortgage.MortgageConditionStatusThrough",
        through_fields=("mortgage_matrix_condition", "amocrm_status"),
        related_name="mortgagematrix_amocrm_statuses",
    )  
    is_there_agent: bool = models.BooleanField(verbose_name="Есть агент", default=False)
    default_value: bool = models.BooleanField(verbose_name="По умолчанию", default=False)

    created_at = models.DateTimeField(verbose_name="Дата и время создания", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Дата и время обновления", auto_now=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        managed = False
        db_table = 'mortgage_calculator_condition_matrix'
        verbose_name = "Матрица условий"
        verbose_name_plural = "21.1. [Справочник] Матрица условий подачи заявки на ипотеку через застройщика"


class MortgageConditionStatusThrough(models.Model):
    """
    Промежуточная таблица матрицы условий к статусам сделок.
    """

    mortgage_matrix_condition: models.ForeignKey = models.ForeignKey(
        to="MortgageConditionMatrix",
        on_delete=models.CASCADE,
        related_name='mortgage_matrix_condition_amocrm_statuses_through',
    )
    amocrm_status: models.ForeignKey = models.ForeignKey(
        to='booking.AmocrmStatus',
        on_delete=models.CASCADE,
        related_name='amocrm_status_matrix_condition_through',
    )

    class Meta:
        managed = False
        db_table = 'mortgage_calсulator_matrix_amocrm_statuses_through'
