from pydantic import Field

from ..entities import BaseMeetingModel


class ResponseMeetingsStatusListModel(BaseMeetingModel):
    """
    Модель статусов мероприятий.
    """

    sort: int
    label: str
    slug: str = Field(..., alias="value")

    class Config:
        allow_population_by_field_name = True
