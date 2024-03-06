from datetime import datetime
from typing import Any

from pydantic import Field, validator

from ..entities import BasePrivilegeCamelCaseModel


class PrivilegeProgramResponse(BasePrivilegeCamelCaseModel):
    """
    Модель ответа программы для категории
    """

    slug: str


class SubcategoryResponse(BasePrivilegeCamelCaseModel):
    slug: str | None
    title: str | None


class PartnerCompanyResponse(BasePrivilegeCamelCaseModel):
    """
    Модель компании
    """

    slug: str
    title: str
    description: str | None
    link: str | None
    image: dict[str, Any] | None

    class Config:
        orm_mode = True


class PrivilegeProgramListResponse(BasePrivilegeCamelCaseModel):
    """
    Модель ответа программы
    """

    slug: str
    # deprecated
    partner_company_id: str

    partner_company: PartnerCompanyResponse
    is_active: bool
    priority_in_subcategory: int
    until: datetime | None
    cooperation_type_id: str
    description: str
    conditions: str
    promocode: str | None
    button_label: str | None
    button_link: str | None
    subcategory: SubcategoryResponse = Field(alias="subcategoryTitle")

    @validator("subcategory")
    def validate_subcategory(cls, subcategory) -> str:
        if subcategory is not None:
            return subcategory.title

    class Config:
        orm_mode = True


class PrivilegeProgramDetailResponse(BasePrivilegeCamelCaseModel):
    """
    Модель детального ответа программы
    """

    slug: str
    # deprecated
    partner_company_id: str

    partner_company: PartnerCompanyResponse
    is_active: bool
    priority_in_subcategory: int
    until: datetime | None
    cooperation_type_id: str
    description: str
    conditions: str
    promocode: str | None
    promocode_rules: str | None
    button_label: str | None
    button_link: str | None
    category_id: str | None
    subcategory: SubcategoryResponse = Field(alias="subcategoryTitle")

    @validator("subcategory")
    def validate_subcategory(cls, subcategory) -> str:
        if subcategory is not None:
            return subcategory.title

    class Config:
        orm_mode = True
