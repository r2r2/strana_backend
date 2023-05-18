from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseQuestionnaireRepo, BaseQuestionnaireModel
from .functional_blocks import FunctionalBlock


class QuestionGroup(BaseQuestionnaireModel):
    """
    Группа вопросов
    """
    id: int = fields.IntField(description='ID', pk=True)
    title: str = fields.CharField(max_length=150, description='Название', null=True)
    func_block: fields.ForeignKeyNullableRelation[FunctionalBlock] = fields.ForeignKeyField(
        on_delete=fields.CASCADE,
        description="Функциональный блок",
        model_name="models.FunctionalBlock",
        related_name="func_block",
        null=True
    )

    question: fields.ForeignKeyNullableRelation['Question']
    user_question_group: fields.ForeignKeyNullableRelation['UserAnswer']

    def __repr__(self):
        return self.title

    class Meta:
        table = "questionnaire_question_groups"


class QuestionGroupRepo(BaseQuestionnaireRepo, ReadWriteMixin):
    """
    Репозиторий группы вопросов
    """
    model = QuestionGroup
