from collections import defaultdict

import structlog

from src.documents.entities import BaseDocumentCase
from src.questionnaire.repos import QuestionnaireUploadDocument, QuestionnaireUploadDocumentRepo


class GetUploadedDocumentsCase(BaseDocumentCase):
    """
    Кейс получения загруженных документов
    """

    def __init__(
        self,
        upload_document_repo: type[QuestionnaireUploadDocumentRepo],
    ):
        self.upload_document_repo: QuestionnaireUploadDocumentRepo = upload_document_repo()

        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)

    async def __call__(self, slugs: str, booking_id: int) -> dict[str, list[QuestionnaireUploadDocument | None]]:
        slugs: list[str] = [slug.strip().lower() for slug in slugs.split(',')]
        self.logger.info(f"Get uploaded documents {slugs=}, {booking_id=}")
        documents: list[QuestionnaireUploadDocument | None] = await self.upload_document_repo.list(
            filters=dict(booking_id=booking_id, uploaded_document__slug__in=slugs),
            related_fields=['uploaded_document'],
        )
        return await self._build_response(documents=documents)

    async def _build_response(
        self,
        documents: list[QuestionnaireUploadDocument | None],
    ) -> dict[str, list[QuestionnaireUploadDocument | None]]:
        """
        Сборка ответа
        """
        response: dict[str, list[QuestionnaireUploadDocument | None]] = defaultdict(list)
        [
            response[doc.uploaded_document.slug].append(doc)
            for doc in documents
        ]
        return response
