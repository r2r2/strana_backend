import asyncio

from common.amocrm import AmoCRM
from src.questionnaire.repos import QuestionnaireUploadDocumentRepo, QuestionnaireUploadDocument
from src.booking.repos import BookingRepo, Booking
from src.booking.exceptions import BookingNotFoundError
from src.task_management.constants import PackageOfDocumentsSlug
from src.task_management.services import UpdateTaskInstanceStatusService
from ..entities import BaseAgentCase
from ..exceptions import UploadDocumentsNotFoundError


class SendUploadDocumentsCase(BaseAgentCase):
    """
    Кейс отправки загруженных документов в АМО
    """
    def __init__(
        self,
        booking_repo: type[BookingRepo],
        upload_document_repo: type[QuestionnaireUploadDocumentRepo],
        amocrm_class: type[AmoCRM],
        update_task_instance_status_service: UpdateTaskInstanceStatusService,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.upload_document_repo: QuestionnaireUploadDocumentRepo = upload_document_repo()
        self.amocrm_class: type[AmoCRM] = amocrm_class
        self.update_task_instance_status_service: UpdateTaskInstanceStatusService = update_task_instance_status_service

    async def __call__(self, *, booking_id: int) -> None:
        booking: Booking = await self.booking_repo.retrieve(filters=dict(id=booking_id))
        if not booking:
            raise BookingNotFoundError

        upload_documents: list[QuestionnaireUploadDocument] = await self.upload_document_repo.list(
            filters=dict(booking_id=booking_id)
        )
        if not upload_documents:
            raise UploadDocumentsNotFoundError

        await self.update_task_instance_status_service(
            booking_id=booking_id, status_slug=PackageOfDocumentsSlug.CHECK.value
        )

        amo_notes: str = "Список загруженных файлов:" + "".join(
            [f'\n"{doc.url}' for doc in upload_documents if doc.url]
        )

        async with await self.amocrm_class() as amocrm:
            await amocrm.send_lead_note(lead_id=booking.amocrm_id, message=amo_notes)
