from django.db import models

from ..entities import BaseQuestionnaireModel


class Matrix(BaseQuestionnaireModel):
    """
    Матрица
    """
    title: str = models.CharField(
        max_length=150,
        verbose_name="Название матрицы",
        null=True,
        blank=True,
        help_text="Определяет список ответов на вопросы, при которых будут выводиться блоки документов",
    )
    conditions = models.ManyToManyField(
        verbose_name="Условия для матрицы",
        to="questionnaire.Condition",
        through="MatrixConditionsThrough",
        through_fields=("matrix", "condition",),
        related_name="matrix_conditions",
        blank=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = "questionnaire_matrix"
        verbose_name = "Матрица"
        verbose_name_plural = " 10.9. [Опросник для пакета документов] Матрицы"
