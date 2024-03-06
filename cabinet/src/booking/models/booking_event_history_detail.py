from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from common.pydantic import CamelCaseBaseModel


class _BookingEventHistoryDetailData(CamelCaseBaseModel):
    id: int
    event_slug: str
    event_name: str
    event_description: Optional[str]
    date_time: datetime
    group_status_until: Optional[str]
    group_status_after: Optional[str]
    task_name_until: Optional[str]
    task_name_after: Optional[str]
    event_status_until: Optional[str]
    event_status_after: Optional[str]


class BookingEventHistories(BaseModel):
    count: int
    result: list[Optional[_BookingEventHistoryDetailData]]
