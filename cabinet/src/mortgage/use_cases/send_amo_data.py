from typing import Any

import structlog
from fastapi import Request
from tortoise.exceptions import IntegrityError

from common.calculator import CalculatorAPI
from common.requests import CommonResponse
from src.mortgage.entities import BaseMortgageCase
from src.mortgage.event_emitter_handlers import mortage_event_emitter
from src.mortgage.models import SendAmoDataSchema
from src.mortgage.repos import PersonalInformationRepo
from src.questionnaire.constants import UploadedFileName
from src.questionnaire.exceptions import QuestionnaireUploadDocumentNotFoundError
from src.questionnaire.repos import QuestionnaireUploadDocumentRepo, QuestionnaireUploadDocument


class SendAmoDataCase(BaseMortgageCase):
    """
    Отправка данных в калькулятор
    """

    def __init__(
        self,
        personal_inf_repo: type[PersonalInformationRepo],
        upload_document_repo: type[QuestionnaireUploadDocumentRepo],
        calculator_api: type[CalculatorAPI],
    ):
        self.personal_inf_repo: PersonalInformationRepo = personal_inf_repo()
        self.upload_document_repo: QuestionnaireUploadDocumentRepo = upload_document_repo()
        self.calculator_api: CalculatorAPI = calculator_api()

        self.payload: SendAmoDataSchema | None = None
        self.authorization: str | None = None
        self.logger: structlog.BoundLogger = structlog.get_logger(self.__class__.__name__)

    async def __call__(self, payload: SendAmoDataSchema, request: Request) -> None:
        self.payload: SendAmoDataSchema = payload
        self.authorization: str = request.headers.get("Authorization")

        await self._create_personal_information()
        await self._add_documents_to_payload()
        await self._send_to_calculator()

    async def _create_personal_information(self) -> None:
        _data: dict[str, Any] = dict(
            booking_id=self.payload.booking_id,
            co_borrowers=self.payload.co_borrowers.co_borrowers,
        )
        _data.update(self.payload.client.dict(exclude_none=True))
        try:
            await self.personal_inf_repo.create(data=_data)
        except IntegrityError as exc:
            self.logger.info(f"Ошибка при создании ПНД формы для ипотеки. {exc=}; {_data=}")
        else:
            self.logger.info(f"Создание ПНД формы для ипотеки. {_data=}")

    async def _send_to_calculator(self) -> None:
        async with self.calculator_api as calculator:
            headers: dict[str, str] = dict(
                Authorization=self.authorization,
            )
            resp: CommonResponse = await calculator.send_amo_data(payload=self.payload, headers=headers)
            if not resp.ok:
                self.logger.info(
                    f"Ошибка при отправке данных в калькулятор. {resp.status=};"
                    f"{self.payload=}"
                )
            else:
                mortage_event_emitter.ee.emit(
                    event='ticket_create',
                    booking_id=self.payload.booking_id,
                    user=None,
                    mortgage_ticket_inform_id=self.payload.mortgage_ticket_id,
                )

    async def _add_documents_to_payload(self) -> None:
        """
        Добавление URL документов в payload
        """
        uploaded_documents: list[QuestionnaireUploadDocument] = await self._get_uploaded_documents()

        for document in uploaded_documents:
            match document.uploaded_document.slug:

                case UploadedFileName.PASSPORT.value:
                    self.payload.documents.passport.append(document.url)

                case UploadedFileName.SNILS.value:
                    self.payload.documents.snils.append(document.url)

                case UploadedFileName.MARRIAGE_CERTIFICATE.value:
                    self.payload.documents.marriage_certificate.append(document.url)

                case UploadedFileName.CHILD_BIRTH_CERTIFICATE.value:
                    self.payload.documents.child_birth_certificate.append(document.url)

                case UploadedFileName.NDFL_2.value:
                    self.payload.documents.ndfl_2.append(document.url)

                case UploadedFileName.LABOR_BOOK.value:
                    self.payload.documents.labor_book.append(document.url)

                case UploadedFileName.CERTIFICATES.value:
                    self.payload.certificates.append(document.url)

                case UploadedFileName.CO_BORROWERS.value:
                    self.payload.co_borrowers.documents.append(document.url)
        self.logger.info(f"Добавлены URL документов в payload. {self.payload=}")

    async def _get_uploaded_documents(self) -> list[QuestionnaireUploadDocument]:
        """
        Получение загруженных документов
        """
        uploaded_documents: list[QuestionnaireUploadDocument | None] = await self.upload_document_repo.list(
            filters=dict(
                mortgage_ticket_id=self.payload.mortgage_ticket_id,
            ),
            related_fields=["uploaded_document"],
        )
        if not uploaded_documents:
            raise QuestionnaireUploadDocumentNotFoundError
        self.logger.info(
            f"Получены загруженные документы для заявки {self.payload.mortgage_ticket_id=}. "
            f"{uploaded_documents=}"
        )
        return uploaded_documents
