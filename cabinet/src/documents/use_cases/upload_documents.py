import asyncio
from typing import Coroutine

import structlog
from fastapi import UploadFile, BackgroundTasks

from common.nextcloud import NextcloudAPI
from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import BookingRepo, Booking
from src.documents.entities import BaseDocumentCase
from src.documents.exceptions import DocumentNotFoundError
from src.questionnaire.repos import (
    QuestionnaireDocumentRepo,
    QuestionnaireUploadDocumentRepo,
    QuestionnaireDocument,
    QuestionnaireUploadDocument,
)


class UploadDocumentsCase(BaseDocumentCase):
    """
    Кейс загрузки документов для ипотеки
    """

    def __init__(
        self,
        booking_repo: type[BookingRepo],
        document_repo: type[QuestionnaireDocumentRepo],
        upload_document_repo: type[QuestionnaireUploadDocumentRepo],
        nextcloud_api: type[NextcloudAPI],
        background_tasks: BackgroundTasks,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.document_repo: QuestionnaireDocumentRepo = document_repo()
        self.upload_document_repo: QuestionnaireUploadDocumentRepo = upload_document_repo()
        self.nextcloud_api: type[NextcloudAPI] = nextcloud_api

        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)
        self.background_tasks: BackgroundTasks = background_tasks

        self.uploaded_documents: list[QuestionnaireUploadDocument] = []
        self.files: list[UploadFile] = []
        self.booking_id: int | None = None
        self.document_id: int | None = None
        self.mortgage_ticket_id: int | None = None

    async def __call__(
        self,
        booking_id: int,
        document_id: int,
        mortgage_ticket_id: int | None = None,
        files: list[UploadFile] | None = None,
    ) -> None:

        self.files: list[UploadFile] | None = files
        self.booking_id: int = booking_id
        self.document_id: int = document_id
        self.mortgage_ticket_id: int | None = mortgage_ticket_id

        self._lead_id: int | None = None
        await self._validate_booking_and_document()
        self.background_tasks.add_task(self._upload_files)

    async def _validate_booking_and_document(self) -> None:
        """
        Валидация бронирования и документа
        Может это и не нужно, но пока оставлю
        """
        booking: Booking = await self.booking_repo.retrieve(filters=dict(id=self.booking_id))
        if not booking:
            raise BookingNotFoundError

        self._lead_id: int = booking.amocrm_id

        document: QuestionnaireDocument = await self.document_repo.retrieve(filters=dict(id=self.document_id))
        if not document:
            raise DocumentNotFoundError
        self.logger.info(
            f"Загружаем документы для бронирования #{self.booking_id}"
            f" и документа: {document.slug}"
        )

    async def _upload_files(self) -> None:
        """
        Загрузка файлов в nextcloud
        """
        await self._check_and_delete_existing_files()
        if not self.files:
            # кейс, когда клиент удалил все файлы из поля загрузки, но они остались в БД
            # их нужно удалить из БД и выйти
            return
        async_tasks: list[Coroutine | None] = []
        async with self.nextcloud_api(lead_id=self._lead_id) as nextcloud_api:
            for file in self.files:
                file_path: str = await nextcloud_api.add_file(file=file)
                async_tasks.append(self._save_uploaded_document(file_path=file_path, file=file))
            async_tasks.append(nextcloud_api.upload_files())
            [
                asyncio.create_task(task)
                for task in async_tasks
            ]
            self.logger.info(f"Загружено {len(self.files)} файла в Nextcloud: {[file.filename for file in self.files]}")

    async def _check_and_delete_existing_files(self) -> None:
        """
        Проверка на существование файлов и удаление их
        """
        if uploaded_documents := await self._check_files_exists():
            self.logger.info(
                f"Удаляем файлы, уже загруженные для бронирования #{self.booking_id} и документа #{self.document_id}",
                files=uploaded_documents
            )
            await self._delete_existing_files(uploaded_documents=uploaded_documents)

    async def _save_uploaded_document(self, file_path: str, file: UploadFile) -> None:
        """
        Сохранение мета инф загруженного документа в БД
        """
        file_data: dict = dict(
            file_name=file.filename,
            uploaded_document_id=self.document_id,
            booking_id=self.booking_id,
            url=file_path,
            mortgage_ticket_id=self.mortgage_ticket_id,
        )
        self.uploaded_documents.append(
            await self.upload_document_repo.create(data=file_data)
        )

    async def _check_files_exists(self) -> list[QuestionnaireUploadDocument | None]:
        """
        Проверка на существование файлов
        """
        uploaded_documents: list[QuestionnaireUploadDocument | None] = await self.upload_document_repo.list(
            filters=dict(
                booking_id=self.booking_id,
                uploaded_document_id=self.document_id,
                mortgage_ticket_id=self.mortgage_ticket_id,
            ),
        )
        return uploaded_documents

    async def _delete_existing_files(self, uploaded_documents: list[QuestionnaireUploadDocument]) -> None:
        """
        Удаление существующих файлов
        """
        [
            await self.upload_document_repo.delete(model=document)
            for document in uploaded_documents
        ]


class UploadDocumentsCaseV2(BaseDocumentCase):
    """
    Кейс загрузки документов для ипотеки
    """

    def __init__(
        self,
        booking_repo: type[BookingRepo],
        document_repo: type[QuestionnaireDocumentRepo],
        upload_document_repo: type[QuestionnaireUploadDocumentRepo],
        nextcloud_api: type[NextcloudAPI],
        background_tasks: BackgroundTasks,
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.document_repo: QuestionnaireDocumentRepo = document_repo()
        self.upload_document_repo: QuestionnaireUploadDocumentRepo = upload_document_repo()
        self.nextcloud_api: type[NextcloudAPI] = nextcloud_api

        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)
        self.background_tasks: BackgroundTasks = background_tasks

        self.uploaded_documents: list[QuestionnaireUploadDocument] = []
        self.files: list[UploadFile] = []
        self.booking_id: int | None = None
        self.document_id: int | None = None
        self.mortgage_ticket_id: int | None = None

    async def __call__(
        self,
        booking_id: int,
        document_id: int,
        mortgage_ticket_id: int | None = None,
        files: list[UploadFile] | None = None,
    ) -> list[QuestionnaireUploadDocument]:

        self.files: list[UploadFile | None] = files if files else []
        self.booking_id: int = booking_id
        self.document_id: int = document_id
        self.mortgage_ticket_id: int | None = mortgage_ticket_id

        self._lead_id: int | None = None
        await self._validate_booking_and_document()
        await self._get_previously_uploaded_documents()
        await self._upload_files()
        return self.uploaded_documents

    async def _validate_booking_and_document(self) -> None:
        """
        Валидация бронирования и документа
        Может это и не нужно, но пока оставлю
        """
        booking: Booking = await self.booking_repo.retrieve(filters=dict(id=self.booking_id))
        if not booking:
            raise BookingNotFoundError

        self._lead_id: int = booking.amocrm_id

        document: QuestionnaireDocument = await self.document_repo.retrieve(filters=dict(id=self.document_id))
        if not document:
            raise DocumentNotFoundError
        self.logger.info(
            f"Загружаем документы для бронирования #{self.booking_id}"
            f" и документа: {document.slug}"
        )

    async def _upload_files(self) -> None:
        """
        Загрузка файлов в nextcloud
        """
        async_tasks: list[Coroutine | None] = []
        async with self.nextcloud_api(lead_id=self._lead_id) as nextcloud_api:
            for file in self.files:
                file_path: str = await nextcloud_api.add_file(file=file)
                async_tasks.append(self._save_uploaded_document(file_path=file_path, file=file))
            async_tasks.append(nextcloud_api.upload_files())
            await asyncio.gather(*async_tasks)
            self.logger.info(f"Загружено {len(self.files)} файла в Nextcloud: {[file.filename for file in self.files]}")

    async def _save_uploaded_document(self, file_path: str, file: UploadFile) -> None:
        """
        Сохранение мета инф загруженного документа в БД
        """
        file_data: dict = dict(
            file_name=file.filename,
            uploaded_document_id=self.document_id,
            booking_id=self.booking_id,
            url=file_path,
            mortgage_ticket_id=self.mortgage_ticket_id,
        )
        self.uploaded_documents.append(
            await self.upload_document_repo.create(data=file_data)
        )

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

