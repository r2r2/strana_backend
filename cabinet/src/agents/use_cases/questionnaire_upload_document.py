from uuid import UUID
from typing import Optional

from fastapi import UploadFile

from common.amocrm import AmoCRMFileUploader
from src.questionnaire.repos import (
    QuestionnaireDocumentRepo,
    QuestionnaireUploadDocumentRepo,
    QuestionnaireDocument,
    QuestionnaireUploadDocument
)
from src.booking.repos import BookingRepo, Booking
from src.booking.exceptions import BookingNotFoundError
from ..entities import BaseAgentCase
from ..exceptions import DocumentNotFoundError


class QuestionareUploadDocumentCase(BaseAgentCase):
    """
    Кейс загрузки документа в амо
    """
    def __init__(
            self,
            booking_repo: type[BookingRepo],
            document_repo: type[QuestionnaireDocumentRepo],
            upload_document_repo: type[QuestionnaireUploadDocumentRepo],
            amocrm_uploader_class: type[AmoCRMFileUploader],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.document_repo: QuestionnaireDocumentRepo = document_repo()
        self.upload_document_repo: QuestionnaireUploadDocumentRepo = upload_document_repo()
        self.amocrm_uploader_class: AmoCRMFileUploader = amocrm_uploader_class()

    async def __call__(
            self,
            *,
            booking_id: int,
            document_id: int,
            file_uuid: Optional[UUID],
            file: UploadFile
    ) -> QuestionnaireUploadDocument:
        booking: Booking = await self.booking_repo.retrieve(filters=dict(id=booking_id))
        if not booking:
            raise BookingNotFoundError

        document: QuestionnaireDocument = await self.document_repo.retrieve(filters=dict(id=document_id))
        if not document:
            raise DocumentNotFoundError

        async with self.amocrm_uploader_class as amocrm_uploader:
            file_url: str = await amocrm_uploader.upload_file(file=file, lead_id=str(booking.amocrm_id))
        file_data: dict = dict(
            file_name=file.filename,
            uploaded_document_id=document_id,
            booking_id=booking_id,
            url=file_url,
        )
        return await self.upload_document_repo.create_or_update(file_uuid=file_uuid, data=file_data)
