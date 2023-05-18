from datetime import date
from typing import Any, Optional

from common.files.models import FileCategoryListModel
from common.pydantic import RecordGetter

from ..constants import AgencyType
from ..entities import BaseAgencyModel


class ActAgencyModel(BaseAgencyModel):
    type: AgencyType.serializer
    name: str

    class Config:
        orm_mode = True


class AgreementStatus(BaseAgencyModel):
    name: str

    class Config:
        orm_mode = True


class ActAgentModel(BaseAgencyModel):
    id: Optional[int]
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    email: Optional[str]
    phone: Optional[str]

    class Config:
        orm_mode = True
        getter_dict = RecordGetter


class ActUserModel(BaseAgencyModel):
    id: Optional[int]
    name: Optional[str]
    surname: Optional[str]
    patronymic: Optional[str]
    phone: Optional[str]
    email: Optional[str]

    class Config:
        orm_mode = True
        getter_dict = RecordGetter


class ActBookingModel(BaseAgencyModel):
    id: Optional[int]
    user: Optional[ActUserModel]

    class Config:
        orm_mode = True


class ResponseAct(BaseAgencyModel):
    id: int
    number: Optional[str]
    status: Optional[AgreementStatus]
    created_at: date
    signed_at: Optional[date]
    template_name: str
    booking_id: int
    agency: ActAgencyModel
    agent: Optional[ActAgentModel]
    files: Optional[list[FileCategoryListModel]]
    user: Optional[ActUserModel]

    class Config:
        orm_mode = True


class ResponseActsListModel(BaseAgencyModel):
    """
    Модель ответа актов пагинация
    """

    count: int
    page_info: dict[str, Any]
    result: list[ResponseAct]

    class Config:
        orm_mode = True


class RequestAgencyActModel(BaseAgencyModel):
    """
    Модель создания договора
    """
    booking_id: int
