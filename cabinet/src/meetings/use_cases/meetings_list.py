from typing import Type

from tortoise.queryset import QuerySet

from common.paginations import PagePagination
from ..repos import Meeting, MeetingRepo
from ..entities import BaseMeetingCase
from ..exceptions import MeetingsNotFoundError


class MeetingsListCase(BaseMeetingCase):
    """
    Кейс для списка встреч
    """
    def __init__(
        self,
        meeting_repo: Type[MeetingRepo],
    ) -> None:
        self.meeting_repo: MeetingRepo = meeting_repo()

    async def __call__(self, *, statuses: list[str], pagination: PagePagination) -> dict:
        filters: dict = dict()
        if statuses:
            filters.update(status__in=statuses)

        meetings_qs: QuerySet = self.meeting_repo.list(filters=filters, start=pagination.start, end=pagination.end)

        meetings: list[Meeting] = await meetings_qs
        if not meetings:
            raise MeetingsNotFoundError

        count: int = await meetings_qs.count()
        data: dict = dict(
            count=count,
            result=meetings,
            page_info=pagination(count=count)
        )
        return data
