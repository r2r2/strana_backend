from typing import Type, Optional, cast

from fastapi import UploadFile

from common.bazis import Bazis
from common.types import IAsyncFile
from common.utils import size_to_byte

from ..constants import OnlinePurchaseSteps, DDU_ALLOWED_FILE_EXTENSIONS
from ..entities import BaseBookingCase
from ..models import ResponseRecognizeDocumentsModel
from ..repos import BookingRepo, Booking
from ..exceptions import (
    BookingNotFoundError,
    BookingWrongStepError
)
from ..validations import DDUUploadFileValidator


class RecognizeDocumentsCase(BaseBookingCase):
    """
    Распознавание документов в Базисе.
    """

    def __init__(self,
                 booking_repo: Type[BookingRepo],
                 bazis_class: Type[Bazis],
                 file_validator: Type[DDUUploadFileValidator]) -> None:
        self.booking_repo: BookingRepo = booking_repo()
        self.bazis_class: Type[Bazis] = bazis_class
        self.file_validator = file_validator()

    async def __call__(
        self, booking_id: int, user_id: int, passport_first_image: IAsyncFile
    ) -> ResponseRecognizeDocumentsModel:
        self._validate_data(passport_image=passport_first_image)
        filters = dict(id=booking_id, user_id=user_id, active=True)
        booking: Optional[Booking] = await self.booking_repo.retrieve(filters=filters)
        if not booking:
            raise BookingNotFoundError

        self._check_step_requirements(booking)

        async with await self.bazis_class() as bazis:
            task_id: Optional[str] = await bazis.upload_files(
                {"passport_first_image": passport_first_image}
            )

        if task_id is None:
            return ResponseRecognizeDocumentsModel.parse_obj(dict(success=False))

        return ResponseRecognizeDocumentsModel.parse_obj(dict(success=True, task_id=task_id))

    def _validate_data(self, passport_image: IAsyncFile) -> None:
        """Валидация фотографии"""

        max_file_size = size_to_byte(mb=10)
        uploaded_file: UploadFile = cast(UploadFile, passport_image)
        self.file_validator.check_file_type(uploaded_file, DDU_ALLOWED_FILE_EXTENSIONS, raise_exception=True)
        self.file_validator.check_file_size(uploaded_file, max_size_bytes=max_file_size, raise_exception=True)

    @classmethod
    def _check_step_requirements(cls, booking: Booking) -> None:
        """Проверка текущего шага."""
        if booking.online_purchase_step() != OnlinePurchaseSteps.DDU_CREATE:
            raise BookingWrongStepError
