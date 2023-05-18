from tortoise.queryset import QuerySet

from src.questionnaire.repos import (
    QuestionnaireDocumentBlock,
    QuestionnaireDocumentBlockRepo,
    QuestionnaireUploadDocumentRepo,
    QuestionnaireDocumentRepo,
    FunctionalBlockRepo,
    FunctionalBlock,
)
from src.booking.repos import BookingRepo, Booking
from src.booking.exceptions import BookingNotFoundError
from ..entities import BaseAgentCase
from ..exceptions import FunctionalBlockNotFoundError


class UploadDocumentsBlocksListCase(BaseAgentCase):
    """
    Кейс получения списка загруженных документов
    """
    def __init__(
            self,
            booking_repo: type[BookingRepo],
            document_block_repo: type[QuestionnaireDocumentBlockRepo],
            document_repo: type[QuestionnaireDocumentRepo],
            upload_document_repo: type[QuestionnaireUploadDocumentRepo],
            functional_block_repo: type[FunctionalBlockRepo],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.document_block_repo: QuestionnaireDocumentBlockRepo = document_block_repo()
        self.document_repo: QuestionnaireDocumentRepo = document_repo()
        self.upload_document_repo: QuestionnaireUploadDocumentRepo = upload_document_repo()
        self.functional_block_repo: FunctionalBlockRepo = functional_block_repo()

    async def __call__(self, *, slug: str, booking_id: int) -> list[QuestionnaireDocumentBlock]:
        booking: Booking = await self.booking_repo.retrieve(filters=dict(id=booking_id))
        if not booking:
            raise BookingNotFoundError

        functional_block: FunctionalBlock = await self.functional_block_repo.retrieve(filters=dict(slug=slug))
        if not functional_block:
            raise FunctionalBlockNotFoundError

        upload_documents_qs: QuerySet = self.upload_document_repo.list(filters=dict(booking_id=booking_id))
        documents_qs: QuerySet = self.document_repo.list(
            prefetch_fields=[
                dict(relation="uploaded_document", queryset=upload_documents_qs, to_attr="attachments")
            ]
        ).distinct()

        # (booking AND slug) + (required OR slug) второе OR отрабатывает всегда
        documents_blocks_filters: dict = dict(
            matrix__conditions__question_groups__func_block__slug=slug,
            matrix__conditions__answers__user_answer__booking_id=booking_id,
        )
        documents_blocks_or_filters: list = [
            dict(matrix__conditions__answers__user_answer__booking_id=booking_id),
            dict(doc_blocks__uploaded_document__booking_id=booking_id),
        ]
        documents_blocks_q_filters: list = [
            self.document_block_repo.q_builder(or_filters=documents_blocks_or_filters)
        ]
        documents_blocks_prefetch: list[dict] = [
            dict(relation="doc_blocks", queryset=documents_qs, to_attr="fields"),
        ]
        documents_blocks_qs: QuerySet = self.document_block_repo.list(
            filters=documents_blocks_filters,
            q_filters=documents_blocks_q_filters,
            prefetch_fields=documents_blocks_prefetch,
        )

        required_blocks_qs: QuerySet = self.document_block_repo.list(
            filters=dict(required=True),
            prefetch_fields=documents_blocks_prefetch
        )

        documents_blocks: list[QuestionnaireDocumentBlock] = await documents_blocks_qs.distinct()

        if not documents_blocks:
            return await required_blocks_qs

        documents_blocks_result: list[QuestionnaireDocumentBlock] = sorted(
            await required_blocks_qs + documents_blocks, key=lambda documents_block: documents_block.sort
        )

        return documents_blocks_result
