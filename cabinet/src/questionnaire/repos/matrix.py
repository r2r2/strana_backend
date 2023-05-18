from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseQuestionnaireRepo, BaseQuestionnaireModel


class Matrix(BaseQuestionnaireModel):
    """
    Матрица
    """
    id: int = fields.IntField(description='ID', pk=True)
    title: str = fields.CharField(max_length=150, description='Название', null=True)
    conditions: fields.ManyToManyRelation["Condition"] = fields.ManyToManyField(
        model_name="models.Condition",
        on_delete=fields.CASCADE,
        description="Условия для матрицы",
        related_name="matrix_conditions",
        through="questionnaire_matrix_conditions",
        backward_key="matrix_id",
        forward_key="condition_id"
    )

    def __repr__(self):
        return self.title

    class Meta:
        table = "questionnaire_matrix"


class MatrixRepo(BaseQuestionnaireRepo, ReadWriteMixin):
    """
    Репозиторий матрицы
    """
    model = Matrix
