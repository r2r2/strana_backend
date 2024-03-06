from collections import defaultdict

import structlog

from common.amocrm import AmoCRM
from src.booking.exceptions import BookingNotFoundError
from src.booking.repos import Booking, BookingRepo
from src.mortgage.entities import BaseMortgageCase
from src.mortgage.exceptions import DocumentsNotFoundError
from src.mortgage.models import SendDDUFormSchema
from src.questionnaire.constants import UploadedFileName
from src.questionnaire.repos import QuestionnaireUploadDocument, QuestionnaireUploadDocumentRepo
from src.task_management.constants import OnlinePurchaseSlug
from src.task_management.services import UpdateTaskInstanceStatusService


class SendDDUFormCase(BaseMortgageCase):
    def __init__(
        self,
        amocrm: type[AmoCRM],
        booking_repo: type[BookingRepo],
        update_task_instance_status_service: UpdateTaskInstanceStatusService,
    ):
        self.amocrm: type[AmoCRM] = amocrm
        self.booking_repo: BookingRepo = booking_repo()
        self.update_task_instance_status_service: UpdateTaskInstanceStatusService = update_task_instance_status_service

        self.payload: SendDDUFormSchema | None = None

        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)

    async def __call__(self, payload: SendDDUFormSchema) -> None:
        self.payload: SendDDUFormSchema = payload
        self.logger.info(f"Отправка формы ПНД в АМО.", payload=self.payload.dict())
        booking: Booking = await self._get_booking()
        await self._send_amo_note(lead_id=booking.amocrm_id)
        await self._update_task_status()

    async def _get_booking(self) -> Booking:
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(id=self.payload.booking_id),
        )
        if not booking:
            raise BookingNotFoundError
        return booking

    async def _send_amo_note(self, lead_id: int) -> None:
        amo_note: str = await self._build_amo_note()
        async with await self.amocrm() as amocrm:
            await amocrm.send_lead_note(
                lead_id=lead_id,
                message=amo_note,
            )
            self.logger.info(f"Заметка отправлена в АМО.", amo_note=amo_note[:120] + '...')

    async def _build_amo_note(self) -> str:
        amo_note_builder: AmoLeadNoteBuilder = AmoLeadNoteBuilder(payload=self.payload)
        message: str = await amo_note_builder.build()
        return message

    async def _update_task_status(self):
        await self.update_task_instance_status_service(
            booking_id=self.payload.booking_id,
            status_slug=OnlinePurchaseSlug.DOCUMENT_VERIFICATION.value,
        )


class AmoLeadNoteBuilder:
    """
    Строитель заметки в АМО
    """
    _DEFAULT_MESSAGE: str = 'Не указано'

    def __init__(
        self,
        payload: SendDDUFormSchema,
    ):
        self.payload: SendDDUFormSchema = payload
        self.message: str = 'Данные для формирования договора получены.'
        self.upload_document_repo: QuestionnaireUploadDocumentRepo = QuestionnaireUploadDocumentRepo()

        self.docs_mapping: dict[str, list[str]] = defaultdict(list)

    async def build(self) -> str:
        uploaded_documents: list[QuestionnaireUploadDocument] = await self._get_uploaded_documents()
        await self._set_docs_mapping(uploaded_documents=uploaded_documents)

        await self._build_personal_data()
        await self._build_documents()
        await self._build_certificates()

        return self.message

    async def _get_uploaded_documents(self) -> list[QuestionnaireUploadDocument]:
        docs: list[QuestionnaireUploadDocument | None] = await self.upload_document_repo.list(
            filters=dict(booking_id=self.payload.booking_id),
            related_fields=["uploaded_document"],
        )
        if not docs:
            raise DocumentsNotFoundError
        return docs

    async def _set_docs_mapping(self, uploaded_documents: list[QuestionnaireUploadDocument]) -> None:
        for doc in uploaded_documents:
            match doc.uploaded_document.slug:
                case UploadedFileName.PASSPORT.value:
                    self.docs_mapping['passport'].append(doc.url)
                case UploadedFileName.SNILS.value:
                    self.docs_mapping['snils'].append(doc.url)
                case UploadedFileName.MARRIAGE_CERTIFICATE.value:
                    self.docs_mapping['marriage_certificate'].append(doc.url)
                case UploadedFileName.CERTIFICATES.value:
                    self.docs_mapping['certificates'].append(doc.url)
                case UploadedFileName.INN.value:
                    self.docs_mapping['inn'].append(doc.url)

    async def _build_personal_data(self) -> None:
        patronymic: str = self.payload.client.patronymic or self._DEFAULT_MESSAGE
        self.message += f"""
            Контактные данные:
            Имя: {self.payload.client.name}
            Фамилия: {self.payload.client.surname}
            Отчество: {patronymic}
            Телефон: {self.payload.client.phone}
            Почта: {self.payload.client.email}
        """

    async def _build_documents(self) -> None:
        passport: list[str] | str = self.docs_mapping.get('passport', self._DEFAULT_MESSAGE)
        snils: list[str] | str = self.docs_mapping.get('snils', self._DEFAULT_MESSAGE)
        marriage_certificate: list[str] | str = self.docs_mapping.get('marriage_certificate', self._DEFAULT_MESSAGE)
        inn: list[str] | str = self.docs_mapping.get('inn', self._DEFAULT_MESSAGE)

        self.message += f"""
            Документы:
            Все страницы паспорта: {passport}
            СНИЛС: {snils}

            Дополнительные документы:
            Свидетельство о браке: {marriage_certificate}
            ИНН: {inn}
        """

    async def _build_certificates(self) -> None:
        certificates: list[str] | str = self.docs_mapping.get('certificates', self._DEFAULT_MESSAGE)
        self.message += f"""
            Сертификаты: {certificates}
        """
