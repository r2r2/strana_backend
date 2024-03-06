from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from common import orm
from ..entities import BaseQuestionnaireRepo, BaseQuestionnaireModel


class QuestionnaireDocumentBlock(BaseQuestionnaireModel):
    """
    Блок документов опросника
    """
    id: int = fields.IntField(description='ID', pk=True)
    title: str = fields.CharField(max_length=150, description='Название', null=True)
    label: str = fields.TextField(description='Подсказка', null=True)
    description: str = fields.TextField(description='Описание подсказки', null=True)
    sort: int = fields.IntField(default=0, description='Приоритет')
    required: bool = fields.BooleanField(description="Не зависит от условий", default=False)
    matrix: fields.ForeignKeyNullableRelation['Matrix'] = fields.ForeignKeyField(
        on_delete=fields.CASCADE,
        description="Матрица",
        model_name="models.Matrix",
        related_name="matrix",
        null=True
    )

    documents: fields.ForeignKeyNullableRelation['QuestionnaireDocument']
    questionnaire_fields: fields.ReverseRelation['QuestionnaireField']

    def __repr__(self):
        return self.title

    class Meta:
        table = "questionnaire_documents_blocks"


class QuestionnaireDocumentBlockRepo(BaseQuestionnaireRepo, ReadWriteMixin):
    """
    Репозиторий блока документа опросника
    """
    model = QuestionnaireDocumentBlock
    q_builder: orm.QBuilder = orm.QBuilder(QuestionnaireDocumentBlock)
