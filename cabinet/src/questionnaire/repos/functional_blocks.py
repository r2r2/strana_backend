from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseQuestionnaireRepo, BaseQuestionnaireModel


class FunctionalBlock(BaseQuestionnaireModel):
    """
    Функциональный блок
    """
    id: int = fields.IntField(description='ID', pk=True)
    title: str = fields.CharField(max_length=150, description='Название', null=True)
    slug: str = fields.CharField(max_length=20, description='Slug')

    question_group: fields.ForeignKeyNullableRelation['QuestionGroup']

    def __repr__(self):
        return self.title


    class Meta:
        table = "questionnaire_func_blocks"


class FunctionalBlockRepo(BaseQuestionnaireRepo, ReadWriteMixin):
    """
    Репозиторий функционального блока
    """
    model = FunctionalBlock
