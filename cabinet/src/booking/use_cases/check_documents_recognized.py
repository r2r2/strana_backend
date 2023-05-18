from typing import Optional, Type

from common.bazis import Bazis, BazisCheckDocumentsReason

from ..constants import OnlinePurchaseSteps
from ..entities import BaseBookingCase
from ..exceptions import BookingNotFoundError, BookingWrongStepError
from ..loggers.wrappers import booking_changes_logger
from ..models import ResponseCheckDocumentsRecognizedModel
from ..repos import Booking, BookingRepo
from ..types import ScannedPassportData


class CheckDocumentsRecognizedCase(BaseBookingCase):
    """
    Распознавание документов в Базисе.
    """

    success_message = "Документы успешно распознаны"
    task_not_found_message = "Произошла ошибка при распознавании документов. Попробуйте ещё раз"
    failed_message = "Произошла ошибка при распознавании документов. Попробуйте ещё раз"
    documents_are_still_recognizing_message = "Документы ещё распознаются"

    def __init__(self, booking_repo: Type[BookingRepo], bazis_class: Type[Bazis]) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.bazis_class: Type[Bazis] = bazis_class
        self.booking_update = booking_changes_logger(self.booking_repo.update, self, content="Распознавание документов")

    async def __call__(
        self, booking_id: int, user_id: int, task_id: str
    ) -> ResponseCheckDocumentsRecognizedModel:
        filters = dict(id=booking_id, user_id=user_id, active=True)
        booking: Optional[Booking] = await self.booking_repo.retrieve(filters=filters)
        if not booking:
            raise BookingNotFoundError

        async with await self.bazis_class() as bazis:
            documents, reason = await bazis.check_documents(task_id=task_id)

        if reason == BazisCheckDocumentsReason.failed:
            return ResponseCheckDocumentsRecognizedModel(
                success=False, recognized=False, reason="failed", message=self.failed_message
            )

        if reason == BazisCheckDocumentsReason.task_not_found:
            return ResponseCheckDocumentsRecognizedModel(
                success=False,
                recognized=False,
                reason="task_not_found",
                message=self.task_not_found_message,
            )

        if reason == BazisCheckDocumentsReason.documents_are_still_recognizing or documents is None:
            return ResponseCheckDocumentsRecognizedModel(
                success=True,
                recognized=False,
                data=documents,
                reason="documents_are_still_recognizing",
                message=self.documents_are_still_recognizing_message,
            )

        scanned_passports_data: Optional[list[ScannedPassportData]] = booking.scanned_passports_data
        if scanned_passports_data is None:
            scanned_passports_data = []

        scanned_passports_data.append(
            ScannedPassportData(
                name=documents["name"],
                surname=documents["surname"],
                patronymic=documents["patronymic"],
                gender=documents["passport_gender"],
            )
        )
        await self.booking_update(
            booking=booking, data=dict(scanned_passports_data=scanned_passports_data)
        )

        return ResponseCheckDocumentsRecognizedModel(
            success=True,
            recognized=True,
            data=documents,
            reason="success",
            message=self.success_message,
        )

    @classmethod
    def _check_step_requirements(cls, booking: Booking) -> None:
        """Проверка текущего шага."""
        if booking.online_purchase_step() != OnlinePurchaseSteps.DDU_CREATE:
            raise BookingWrongStepError
