from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from pytz import UTC

from .common import AmoModel, EmbeddedDTO


class AmoContactLead(BaseModel):
    id: int


class AmoContactCompany(BaseModel):
    id: int


class AmoContactCustomer(BaseModel):
    id: int


class AmoContactEmbedded(EmbeddedDTO):
    leads: Optional[list[AmoContactLead]] = []
    companies: Optional[list[AmoContactCompany]] = []
    customers: Optional[list[AmoContactCustomer]] = []


class AmoContact(AmoModel):
    """
    Контакт из Амо
    """

    id: int
    name: Optional[str]
    company_id: Optional[int]
    responsible_user_id: Optional[int]
    group_id: Optional[int]
    created_by: Optional[int]
    updated_by: Optional[int]
    created_at: int = Field(default=int(datetime.now(tz=UTC).timestamp()))
    updated_at: int = Field(default=int(datetime.now(tz=UTC).timestamp()))
    closest_task_at: Optional[int]
    is_deleted: Optional[bool]
    is_unsorted: Optional[bool]
    account_id: Optional[int]
    embedded: Optional[AmoContactEmbedded] = Field({}, alias='_embedded')
