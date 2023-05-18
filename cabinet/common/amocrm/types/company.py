from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field
from pytz import UTC

from .common import AmoModel, EmbeddedDTO


class AmoCompanyLead(BaseModel):
    id: int


class AmoCompanyCustomer(BaseModel):
    id: int


class AmoCompanyContact(BaseModel):
    id: int


class AmoCompanyCatalogElement(BaseModel):
    id: int
    metadata: dict
    quantity: Union[int, float]
    catalog_id: int
    price_id: int


class AmoCompanyEmbedded(EmbeddedDTO):
    leads: Optional[list[AmoCompanyLead]] = []
    customers: Optional[list[AmoCompanyCustomer]] = []
    contacts: Optional[list[AmoCompanyContact]] = []
    catalog_elements: Optional[list[AmoCompanyCatalogElement]] = []


class AmoCompany(AmoModel):
    """
    Компания из Амо
    """

    id: Optional[int] = None
    name: str = ''
    responsible_user_id: Optional[int]
    group_id: Optional[int]
    created_by: Optional[int]
    updated_by:  Optional[int]
    created_at: int = Field(default=int(datetime.now(tz=UTC).timestamp()))
    updated_at: int = Field(default=int(datetime.now(tz=UTC).timestamp()))
    closest_task_at: Optional[int]
    is_deleted: bool = False
    embedded: Optional[AmoCompanyEmbedded] = Field(AmoCompanyEmbedded(), alias='_embedded')
