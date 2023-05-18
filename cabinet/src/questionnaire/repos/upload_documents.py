from uuid import uuid4, UUID

from tortoise import fields

from common.orm.mixins import ReadWriteMixin
from ..entities import BaseQuestionnaireRepo, BaseQuestionnaireModel


class QuestionnaireUploadDocument(BaseQuestionnaireModel):
    """
    Загруженный документ опросника
    """
    id: UUID = fields.UUIDField(pk=True, default=uuid4, description='UID')
    file_name: str = fields.CharField(max_length=150, description='Название файла', null=True)
    url = fields.CharField(max_length=2083, description="URL загруженного файла", null=True)
    uploaded_document: fields.ForeignKeyNullableRelation['QuestionnaireDocument'] = fields.ForeignKeyField(
        on_delete=fields.SET_NULL,
        description="Документы",
        model_name="models.QuestionnaireDocument",
        related_name="uploaded_document",
        null=True
    )
    booking: fields.ForeignKeyNullableRelation['Booking'] = fields.ForeignKeyField(
        on_delete=fields.SET_NULL,
        description="Сделка",
        model_name="models.Booking",
        related_name="booking",
        null=True,
    )

    def __repr__(self):
        return self.file_name


    class Meta:
        table = "questionnaire_upload_documents"


class QuestionnaireUploadDocumentRepo(BaseQuestionnaireRepo, ReadWriteMixin):
    """
    Репозиторий загруженного документа опросника
    """
    model = QuestionnaireUploadDocument

    async def create_or_update(self, file_uuid: UUID, data: dict) -> QuestionnaireUploadDocument:
        """
        Получение или создание загруженного документа
        """
        if file_uuid:
            model: QuestionnaireUploadDocument = await self.model.get(id=file_uuid)
        else:
            model: QuestionnaireUploadDocument = await self.model.create(**data)
        return model
