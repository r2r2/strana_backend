from datetime import datetime
from typing import Optional, Any

from src.dashboard import constants as dashboard_constants
from src.dashboard.entities import BaseDashboardModel


class _ElementRetrieveModel(BaseDashboardModel):
    id: int
    type: str
    width: Optional[dashboard_constants.WidthType.serializer]
    title: Optional[str]
    description: Optional[str]
    image: Optional[dict[str, Any]]
    link: Optional[list[str]]
    expires: Optional[datetime]

    class Config:
        orm_mode = True


class BlockListResponse(BaseDashboardModel):
    id: int
    type: Optional[str]
    width: Optional[int]
    title: Optional[str]
    description: Optional[str]
    image: Optional[dict[str, Any]]
    elements_list: list[_ElementRetrieveModel]

    class Config:
        orm_mode = True
