from uuid import UUID

from tortoise.queryset import QuerySet

from src.questionnaire.repos import QuestionnaireUploadDocumentRepo
from ..entities import BaseAgentCase


class DeleteUploadDocumentsCase(BaseAgentCase):
    """
    Кейс удаления загруженных документов
    """
    def __init__(
        self,
        upload_document_repo: type[QuestionnaireUploadDocumentRepo],
    ) -> None:
        self.upload_document_repo: QuestionnaireUploadDocumentRepo = upload_document_repo()

    async def __call__(self, *, upload_documents_ids: list[UUID], agent_id: int) -> None:
        filters: dict = dict(id__in=upload_documents_ids, booking__agent_id=agent_id)
        upload_documents_qs: QuerySet = self.upload_document_repo.list(filters=filters)

        async for upload_document in upload_documents_qs:
            await upload_document.delete()
