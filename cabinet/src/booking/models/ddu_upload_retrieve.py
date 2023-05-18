from typing import Optional

from common.files.models import FileCategoryListModel

from ..entities import BaseBookingModel


class _BookingUserRetrieveModel(BaseBookingModel):
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]

    class Config:
        orm_mode = True


class ResponseDDUUploadRetrieveModel(BaseBookingModel):
    """
    Модель ответа на запрос загрузки ДДУ юристом.

    Возвращаются данные бронирования.
    """

    user: Optional[_BookingUserRetrieveModel]
    files: list[FileCategoryListModel]
    amocrm_ddu_uploaded_by_lawyer: bool

    class Config:
        orm_mode = True
