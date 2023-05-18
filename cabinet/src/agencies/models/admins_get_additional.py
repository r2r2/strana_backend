from typing import Any, Optional
from pydantic import Field
from datetime import date

from common.files.models import FileCategoryListModel

from ..constants import AgencyType
from ..entities import BaseAgencyModel


class AdditionalAgreementStatus(BaseAgencyModel):
    name: str

    class Config:
        orm_mode = True


class Agency(BaseAgencyModel):
    id: int
    type: AgencyType.serializer
    name: str
    inn: str

    class Config:
        orm_mode = True


class ResponseAdminsAdditionalAgreement(BaseAgencyModel):
    id: int
    number: Optional[str]
    status: Optional[AdditionalAgreementStatus]
    created_at: date = Field(alias="createdAt")
    template_name: Optional[str] = Field(alias="templateName")
    booking_id: Optional[int] = Field(alias="bookingId")
    agency: Agency
    project_id: int = Field(alias="projectId")
    reason_comment: str = Field(alias="reasonComment")
    files: Optional[list[FileCategoryListModel]]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ResponseAdminsAdditionalAgreementList(BaseAgencyModel):
    """
    Модель ответа дополнительных соглашений с пагинацией
    """
    count: int
    page_info: dict[str, Any]
    result: list[ResponseAdminsAdditionalAgreement]

    class Config:
        orm_mode = True
