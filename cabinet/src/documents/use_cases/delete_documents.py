import asyncio
from typing import Coroutine

import structlog
from fastapi import BackgroundTasks

from common.nextcloud import NextcloudAPI
from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import BookingRepo
from src.documents.entities import BaseDocumentCase
from src.documents.models import RequestDeleteDocumentsSchema
from src.questionnaire.repos import (
    QuestionnaireDocumentRepo,
    QuestionnaireUploadDocumentRepo,
    QuestionnaireUploadDocument,
)


class DeleteDocumentsCase(BaseDocumentCase):
    """
    Кейс удаления документов по ID
    """

    def __init__(
        self,
        booking_repo: type[BookingRepo],
        document_repo: type[QuestionnaireDocumentRepo],
        upload_document_repo: type[QuestionnaireUploadDocumentRepo],
        nextcloud_api: type[NextcloudAPI],
        background_tasks: BackgroundTasks,
    ):
        self.booking_repo: BookingRepo = booking_repo()
        self.document_repo: QuestionnaireDocumentRepo = document_repo()
        self.upload_document_repo: QuestionnaireUploadDocumentRepo = upload_document_repo()
        self.nextcloud_api: type[NextcloudAPI] = nextcloud_api
        self.background_tasks: BackgroundTasks = background_tasks

        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)
        self.payload: RequestDeleteDocumentsSchema | None = None

    async def __call__(self, payload: RequestDeleteDocumentsSchema) -> list[QuestionnaireUploadDocument | None]:
        self.payload: RequestDeleteDocumentsSchema = payload

        await self._process_delete_in_nextcloud()
        await self._delete_documents_in_cabinet()

        return await self._get_remaining_documents()

    async def _process_delete_in_nextcloud(self) -> None:
        """
        Удаление документов в Nextcloud
        """
        lead_id: int = await self._get_booking_amocrm_id()
        file_urls: list[str] = await self._get_file_urls()
        self.background_tasks.add_task(self._delete_files_in_nextcloud, file_urls=file_urls, lead_id=lead_id)

    async def _delete_files_in_nextcloud(self, file_urls: list[str], lead_id: int) -> None:
        """
        Удаление файлов в Nextcloud
        """
        async with self.nextcloud_api(lead_id=lead_id) as nextcloud_api:
            async_tasks: list[Coroutine] = [
                nextcloud_api.delete_file(url=url)
                for url in file_urls
            ]
            await asyncio.gather(*async_tasks, return_exceptions=True)

    async def _get_booking_amocrm_id(self) -> int:
        """
        Получение ID сделки
        """
        booking: dict[str, int] = await self.booking_repo.retrieve(
            filters=dict(id=self.payload.booking_id),
        ).values("amocrm_id")
        if not booking:
            raise BookingNotFoundError
        return booking["amocrm_id"]

    async def _get_file_urls(self) -> list[str]:
        """
        Получение URL файлов
        """
        file_urls: list[str] = await self.upload_document_repo.list(
            filters=dict(id__in=self.payload.file_ids),
        ).values_list("url", flat=True)
        return file_urls

    async def _delete_documents_in_cabinet(self) -> None:
        """
        Удаление документов
        """
        self.logger.info(f"Deleting documents with ids: {self.payload.file_ids=}")
        await QuestionnaireUploadDocument.filter(id__in=self.payload.file_ids).delete()

    async def _get_remaining_documents(self) -> list[QuestionnaireUploadDocument | None]:
        """
        Получение оставшихся документов
        """
        filters: dict[str, int] = dict(
            booking_id=self.payload.booking_id,
            uploaded_document_id=self.payload.document_id,
        )
        return await self.upload_document_repo.list(filters=filters)
