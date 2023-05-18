from typing import Any, Type

from common.amocrm import AmoCRM
from common.files import FileCategory, FileContainer, ProcessedFile
from common.utils import size_to_byte
from fastapi import UploadFile

from ..constants import (DDU_ALLOWED_FILE_EXTENSIONS, BookingFileType,
                         OnlinePurchaseSteps, UploadPath)
from ..entities import BaseBookingCase
from ..exceptions import BookingNotFoundError, BookingWrongStepError
from ..loggers.wrappers import booking_changes_logger
from ..repos import Booking, BookingRepo, DDURepo
from ..repos.booking_history import BookingHistoryDocument
from ..services import HistoryService
from ..types import BookingFileProcessor
from ..validations import DDUUploadFileValidator


def get_category(files: FileContainer, category_name: str) -> FileCategory:
    return next(filter(lambda category: category.slug == category_name, files))


class EscrowUploadCase(BaseBookingCase):
    """
    Выбор способа покупки
    """

    _history_template = "src/booking/templates/history/escrow_upload.txt"

    def __init__(
        self,
        booking_repo: Type[BookingRepo],
        ddu_repo: Type[DDURepo],
        file_processor: BookingFileProcessor,
        amocrm_class: Type[AmoCRM],
        history_service: HistoryService,
        file_validator: Type[DDUUploadFileValidator],
    ) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.ddu_repo: DDURepo = ddu_repo()
        self.file_processor: BookingFileProcessor = file_processor
        self.file_validator: DDUUploadFileValidator = file_validator()
        self.amocrm_class: Type[AmoCRM] = amocrm_class

        self._history_service = history_service
        self.booking_update = booking_changes_logger(self.booking_repo.update, self, content="Выбор способа покупки")

    async def __call__(self, booking_id: int, user_id: int, escrow_file: Any) -> Booking:
        self._validate(escrow_file=escrow_file)
        filters = dict(active=True, id=booking_id, user_id=user_id)
        booking = await self.booking_repo.retrieve(
            filters=filters,
            related_fields=["project", "property", "floor", "building", "ddu"],
            prefetch_fields=["ddu__participants"],
        )
        if not booking:
            raise BookingNotFoundError

        previous_online_purchase_step = booking.online_purchase_step()
        self._check_requirements(booking=booking)

        data = dict(escrow_uploaded=True)
        data["files"] = await self.file_processor(
            files={BookingFileType.ESCROW: [escrow_file]},
            path=UploadPath.BOOKING_FILES,
            choice_class=BookingFileType,
            container=booking.files,
            filter_by_hash=False,
        )

        booking = await self.booking_update(booking=booking, data=data)
        # await self._amocrm_hook(booking)

        escrow_file: BookingHistoryDocument = {
            "name": "Документ об открытии эскроу-счёта",
            "size": self._get_escrow_file(booking).bytes_size,
            "url": self._get_escrow_file(booking).aws,
        }

        await self._history_service.execute(
            booking=booking,
            previous_online_purchase_step=previous_online_purchase_step,
            template=self._history_template,
            documents=[[escrow_file]],
        )

        return booking

    def _validate(self, escrow_file: UploadFile):
        max_size_bytes = size_to_byte(mb=15)
        self.file_validator.check_file_type(escrow_file, DDU_ALLOWED_FILE_EXTENSIONS, raise_exception=True)
        self.file_validator.check_file_size(escrow_file, max_size_bytes=max_size_bytes, raise_exception=True)

    async def _amocrm_hook(self, booking: Booking) -> None:
        """
        ✅ После отправки документа об открытии эскроу-счета клиентом
        в сделке AMO CRM создать примечание с текстом:
            Клиент прикрепил документ об открытии эскроу-счета в банке.
            Ссылка на документ - $ссылка
        """
        async with await self.amocrm_class() as amocrm:
            await amocrm.create_note(
                lead_id=booking.amocrm_id,
                text=self._get_note_text(booking),
                element="lead",
                note="common",
            )

    @classmethod
    def _get_note_text(cls, booking: Booking) -> str:
        """Текст примечания."""
        escrow_url = cls._get_escrow_file(booking).aws
        template = (
            "Клиент прикрепил документ об открытии эскроу-счета в банке. Ссылка на документ - {}"
        )
        return template.format(escrow_url)

    @classmethod
    def _get_escrow_file(cls, booking: Booking) -> ProcessedFile:
        """Файл эскроу-счёта."""
        return get_category(booking.files, BookingFileType.ESCROW)[-1]

    @classmethod
    def _check_requirements(cls, *, booking: Booking) -> None:
        """Проверка на выполнение условий."""
        if booking.online_purchase_step() != OnlinePurchaseSteps.ESCROW_UPLOAD:
            raise BookingWrongStepError
