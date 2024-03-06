import asyncio
from uuid import UUID
from typing import Optional, Coroutine

import structlog
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
        file: UploadFile,
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


class QuestionareUploadDocumentCaseV2(BaseAgentCase):
    """
    Кейс загрузки документов в амо
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

        self.booking_id: int | None = None
        self.document_id: int | None = None
        self.files: list[UploadFile] | None = None
        self.uploaded_files: tuple[str] | None = None
        self.uploaded_documents: list[QuestionnaireUploadDocument | None] = []
        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)

    async def __call__(
        self,
        *,
        booking_id: int,
        document_id: int,
        files: list[UploadFile],
    ) -> list[QuestionnaireUploadDocument | None]:
        self.booking_id: int = booking_id
        self.document_id: int = document_id
        self.files: list[UploadFile] = files

        booking, _ = await self._get_booking_and_document()

        await self._upload_files_to_amocrm(booking=booking)
        await self._get_previously_uploaded_documents()
        await self._process_uploaded_documents()
        return self.uploaded_documents

    async def _get_booking_and_document(self) -> tuple[Booking, QuestionnaireDocument]:
        """
        Получение бронирования и документа
        """
        booking: Booking = await self.booking_repo.retrieve(filters=dict(id=self.booking_id))
        if not booking:
            raise BookingNotFoundError

        document: QuestionnaireDocument = await self.document_repo.retrieve(filters=dict(id=self.document_id))
        if not document:
            raise DocumentNotFoundError
        return booking, document
    
    async def _upload_files_to_amocrm(self, booking: Booking) -> None:
        """
        Загрузка файлов в амо
        """
        rate_limit: int = 3
        req_counter: int = 0
        semaphore: asyncio.Semaphore = asyncio.Semaphore(rate_limit)

        async def upload_file_with_limit(sem, file, amo_uploader) -> str:
            nonlocal req_counter
            if req_counter >= rate_limit:
                await asyncio.sleep(1)
            req_counter += 1
            async with sem:
                file_url: str = await amo_uploader.upload_file(file=file, lead_id=str(booking.amocrm_id))
            req_counter -= 1
            return file_url

        async with self.amocrm_uploader_class as amo_uploader:
            tasks: list[Coroutine | None] = [
                upload_file_with_limit(semaphore, file, amo_uploader) 
                for file in self.files
            ]
            self.uploaded_files: tuple[str] | None = await asyncio.gather(*tasks, return_exceptions=True)
        self.logger.info(f"Загружено {len(self.files)} файла в амо: {[file.filename for file in self.files]}")

    async def _process_uploaded_documents(self) -> None:
        """
        Создание или обновление загруженных документов
        """
        files_data: list[dict] = [
            dict(
                file_name=file.filename,
                uploaded_document_id=self.document_id,
                booking_id=self.booking_id,
                url=file_url,
            )
            for file, file_url in zip(self.files, self.uploaded_files)
        ]
        async_tasks: list[Coroutine | None] = [
            self._get_or_create_uploaded_document(data)
            for data in files_data
        ]
        await asyncio.gather(*async_tasks)

    async def _get_or_create_uploaded_document(self, data: dict) -> None:
        """
        Обработка загруженного документа
        """
        filters: dict = dict(
            file_name=data['file_name'],
            uploaded_document_id=self.document_id,
            booking_id=self.booking_id,
        )
        uploaded_document: QuestionnaireUploadDocument | None = await self.upload_document_repo.retrieve(
            filters=filters,
        )
        if not uploaded_document:
            uploaded_document: QuestionnaireUploadDocument = await self.upload_document_repo.create(data=data)
            self.logger.info(f"Создан загруженный документ: {uploaded_document.file_name}; UUID={uploaded_document.id}")

        if uploaded_document not in self.uploaded_documents:
            self.uploaded_documents.append(uploaded_document)
        
    async def _get_previously_uploaded_documents(self) -> None:
        """
        Получение ранее загруженных документов
        """
        uploaded_documents: list[QuestionnaireUploadDocument] = await self.upload_document_repo.list(
            filters=dict(
                uploaded_document_id=self.document_id,
                booking_id=self.booking_id,
            ),
        )
        self.uploaded_documents.extend(uploaded_documents)
        self.logger.info(f"Получено {len(uploaded_documents)} ранее загруженных документов")
