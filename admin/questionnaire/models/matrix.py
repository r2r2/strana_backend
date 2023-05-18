from django.db import models

from ..entities import BaseQuestionnaireModel


class Matrix(BaseQuestionnaireModel):
    """
    Матрица
    """
    title: str = models.CharField(
        max_length=150, verbose_name="Название матрицы", help_text="Название матрицы", null=True, blank=True
    )
    conditions = models.ManyToManyField(
        null=True, blank=True,
        verbose_name="Условия для матрицы",
        to="questionnaire.Condition",
        through="MatrixConditionsThrough",
        through_fields=("matrix", "condition",),
        related_name="matrix_conditions"
    )

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = "questionnaire_matrix"
        verbose_name = "Матрица"
        verbose_name_plural = "Матрицы"
