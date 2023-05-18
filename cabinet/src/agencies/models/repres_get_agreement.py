from datetime import date
from typing import Any, Optional

from common.files.models import FileCategoryListModel

from ..constants import AgencyType
from ..entities import BaseAgencyModel


class AgreementsAgencyModel(BaseAgencyModel):
    type: AgencyType.serializer
    name: str


class AgreementStatus(BaseAgencyModel):
    name: str


class AgreementType(BaseAgencyModel):
    name: str


class ResponseRepresAgreement(BaseAgencyModel):
    id: int
    number: Optional[str]
    status: Optional[AgreementStatus]
    created_at: date
    signed_at: Optional[date]
    template_name: str
    booking_id: int
    agency: AgreementsAgencyModel
    project_id: int
    agreement_type: Optional[AgreementType]
    files: Optional[list[FileCategoryListModel]]

    class Config:
        orm_mode = True


class ResponseRepresAgreementList(BaseAgencyModel):
    """
    Модель ответа договоров пагинация
    """
    count: int
    page_info: dict[str, Any]
    result: list[ResponseRepresAgreement]

    class Config:
        orm_mode = True
