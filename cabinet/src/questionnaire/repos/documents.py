from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseQuestionnaireRepo, BaseQuestionnaireModel


class QuestionnaireDocument(BaseQuestionnaireModel):
    """
    Документ сделки
    """
    id: int = fields.IntField(description='ID', pk=True)
    label: str = fields.CharField(max_length=150, description='Название', null=True)
    required: bool = fields.BooleanField(description="Обязательный", default=True)
    doc_blocks: fields.ForeignKeyNullableRelation['QuestionnaireDocumentBlock'] = fields.ForeignKeyField(
        on_delete=fields.CASCADE,
        description="Блоки документов",
        model_name="models.QuestionnaireDocumentBlock",
        related_name="doc_blocks",
        null=True
    )
    sort: int = fields.IntField(default=0, description='Приоритет')

    uploaded_documents: fields.ForeignKeyNullableRelation['QuestionnaireUploadDocument']

    def __repr__(self):
        return self.label


    class Meta:
        table = "questionnaire_documents"


class QuestionnaireDocumentRepo(BaseQuestionnaireRepo, ReadWriteMixin):
    """
    Репозиторий документа сделки
    """
    model = QuestionnaireDocument
