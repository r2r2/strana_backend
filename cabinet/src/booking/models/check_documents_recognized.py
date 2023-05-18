from datetime import date
from typing import Optional, Literal

from src.booking.entities import BaseBookingModel


class RecognizedData(BaseBookingModel):
    passport_serial: Optional[str]
    passport_number: Optional[str]
    passport_issued_by: Optional[str]
    passport_department_code: Optional[str]
    passport_issued_date: Optional[date]

    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    passport_birth_date: Optional[date]
    passport_birth_place: Optional[str]
    passport_gender: Optional[Literal["male", "female"]]


class ResponseCheckDocumentsRecognizedModel(BaseBookingModel):
    """
    Ответ на запрос проверки распознавания документов в БАЗИС-е
    """

    success: bool
    message: str
    reason: Literal["success", "documents_are_still_recognizing", "task_not_found", "failed"]
    data: Optional[RecognizedData]
