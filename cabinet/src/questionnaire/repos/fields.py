from tortoise import fields

from common.orm.mixins import CRUDMixin
from src.questionnaire.entities import BaseQuestionnaireModel, BaseQuestionnaireRepo


class QuestionnaireField(BaseQuestionnaireModel):
    """
    12.11 Поля
    """
    id: int = fields.IntField(description='ID', pk=True)
    slug: str = fields.CharField(max_length=255, description='Слаг', null=True)
    name: str = fields.CharField(max_length=255, description='Название', null=True)
    type: str = fields.CharField(max_length=255, description='Тип', null=True)
    description: str = fields.TextField(description='Описание', null=True)
    block: fields.ForeignKeyNullableRelation['QuestionnaireDocumentBlock'] = fields.ForeignKeyField(
        on_delete=fields.CASCADE,
        description="Блок",
        model_name="models.QuestionnaireDocumentBlock",
        related_name="questionnaire_fields",
        null=True
    )

    def __repr__(self) -> str:
        return self.name

    class Meta:
        table = "questionnaire_fields"


class QuestionnaireFieldRepo(BaseQuestionnaireRepo, CRUDMixin):
    """
    Репозиторий полей
    """
    model = QuestionnaireField
