from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseQuestionnaireRepo, BaseQuestionnaireModel


class Answer(BaseQuestionnaireModel):
    """
    Ответ
    """
    id: int = fields.IntField(description='ID', pk=True)
    title: str = fields.CharField(max_length=150, description='Название', null=True)
    description: str = fields.TextField(description='Тело ответа', null=True)
    hint: str = fields.TextField(description='Подсказка', null=True)
    is_active: bool = fields.BooleanField(description="Активность", default=True)
    is_default: bool = fields.BooleanField(description="Ответ по умолчанию", default=True)
    question: fields.ForeignKeyNullableRelation['Question'] = fields.ForeignKeyField(
        on_delete=fields.CASCADE,
        description="Вопросы",
        model_name="models.Question",
        related_name="answers",
        null=True
    )
    sort: int = fields.IntField(default=0, description='Приоритет')

    def __repr__(self):
        return self.title

    class Meta:
        table = "questionnaire_answers"


class AnswerRepo(BaseQuestionnaireRepo, ReadWriteMixin):
    """
    Репозиторий ответа
    """
    model = Answer
