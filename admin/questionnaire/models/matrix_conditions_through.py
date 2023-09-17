from django.db import models


class MatrixConditionsThrough(models.Model):
    matrix = models.OneToOneField(
        verbose_name="Матрица",
        to="questionnaire.Matrix",
        on_delete=models.CASCADE,
        related_name="matrix",
        primary_key=True
    )
    condition = models.ForeignKey(
        verbose_name="Условие",
        to="questionnaire.Condition",
        on_delete=models.CASCADE,
        related_name="condition",
        unique=False,
    )

    class Meta:
        managed = False
        db_table = "questionnaire_matrix_conditions"
        unique_together = ('matrix', 'condition')
        verbose_name = "Матрица-Условие"
        verbose_name_plural = "Матрицы-Условия"

    def __str__(self):
        return f"{self.matrix} {self.condition}"
