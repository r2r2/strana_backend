from typing import Optional

from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseQuestionnaireRepo, BaseQuestionnaireModel
from ..constants import QuestionType


class Question(BaseQuestionnaireModel):
    """
    Вопрос
    """
    id: int = fields.IntField(description='ID', pk=True)
    title: str = fields.CharField(max_length=150, description='Название', null=True)
    description: str = fields.TextField(description='Тело вопроса', null=True)
    is_active: bool = fields.BooleanField(description="Активность", default=True)
    type: Optional[str] = fields.CharEnumField(
        QuestionType, description="Тип", max_length=10, default=QuestionType.SINGLE
    )
    required: bool = fields.BooleanField(description="Обязателен к ответу", default=True)
    question_group: fields.ForeignKeyNullableRelation['QuestionGroup'] = fields.ForeignKeyField(
        on_delete=fields.CASCADE,
        description="Группа вопроса",
        model_name="models.QuestionGroup",
        related_name="question_group",
        null=True
    )
    sort: int = fields.IntField(default=0, description='Приоритет')

    answers: fields.ForeignKeyNullableRelation['Answer']
    user_question: fields.ForeignKeyNullableRelation['UserAnswer']

    def __repr__(self):
        return self.title

    class Meta:
        table = "questionnaire_questions"


class QuestionRepo(BaseQuestionnaireRepo, ReadWriteMixin):
    """
    Репозиторий вопросов
    """
    model = Question
