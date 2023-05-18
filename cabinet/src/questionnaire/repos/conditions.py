from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseQuestionnaireRepo, BaseQuestionnaireModel


class Condition(BaseQuestionnaireModel):
    """
    Условие для матрицы
    """
    id: int = fields.IntField(description='ID', pk=True)
    title: str = fields.CharField(max_length=150, description='Название', null=True)
    question_groups: fields.ForeignKeyNullableRelation['QuestionGroup'] = fields.ForeignKeyField(
        on_delete=fields.CASCADE,
        description="Группы вопросов",
        model_name="models.QuestionGroup",
        related_name="condition_question_groups",
        null=True
    )
    questions: fields.ForeignKeyNullableRelation['Question'] = fields.ForeignKeyField(
        on_delete=fields.CASCADE,
        description="Вопросы",
        model_name="models.Question",
        related_name="condition_questions",
        null=True
    )
    answers: fields.ForeignKeyNullableRelation['Answer'] = fields.ForeignKeyField(
        on_delete=fields.CASCADE,
        description="Ответы",
        model_name="models.Answer",
        related_name="condition_answers",
        null=True
    )

    matrix: fields.ManyToManyRelation['Matrix']

    def __repr__(self):
        return self.title

    class Meta:
        table = "questionnaire_conditions"


class ConditionRepo(BaseQuestionnaireRepo, ReadWriteMixin):
    """
    Репозиторий условия для матрицы
    """
    model = Condition
