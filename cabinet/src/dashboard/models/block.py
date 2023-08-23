from datetime import datetime
from typing import Optional, Any, Union

from src.dashboard.entities import BaseDashboardModel


class _ElementRetrieveModel(BaseDashboardModel):
    id: Union[int, str]
    type: str
    width: Optional[int]
    title: Optional[str]
    description: Optional[str]
    image: Optional[dict[str, Any]]
    link: Optional[str]
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
