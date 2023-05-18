from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field
from pytz import UTC

from .common import AmoModel, EmbeddedDTO


class AmoLeadLossReason(BaseModel):
    id: int
    name: str


class AmoLeadContact(BaseModel):
    id: int
    is_main: bool


class AmoLeadCompany(BaseModel):
    id: int


class AmoLeadCatalogElement(BaseModel):
    id: int
    metadata: dict
    quantity: Union[int, float]
    catalog_id: int
    price_id: int


class AmoLeadEmbedded(EmbeddedDTO):
    loss_reason: Optional[AmoLeadLossReason] = None
    contacts: Optional[list[AmoLeadContact]] = []
    companies: Optional[list[AmoLeadCompany]] = []
    catalog_elements: Optional[list[AmoLeadCatalogElement]] = []


class AmoLead(AmoModel):
    """
    Сделка из Амо.
    """

    id: Optional[int]
    name: str = ''
    price: Optional[float]
    responsible_user_id: Optional[int]
    group_id: Optional[int]
    status_id: Optional[int]
    pipeline_id: Optional[int]
    loss_reason_id: Optional[int]
    created_by: Optional[int]
    updated_by: Optional[int]
    closed_at: Optional[int]
    updated_at: int = Field(default=int(datetime.now(tz=UTC).timestamp()))
    created_at: int = Field(default=int(datetime.now(tz=UTC).timestamp()))
    closed_by: Optional[int]
    closest_task_at: Optional[int]
    is_deleted: bool = False
    scope: Optional[int]
    account_id: Optional[int]
    embedded: Optional[AmoLeadEmbedded] = Field(AmoLeadEmbedded(), alias='_embedded')
