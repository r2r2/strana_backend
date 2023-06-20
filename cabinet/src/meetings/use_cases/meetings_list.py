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

    async def __call__(self, *, statuses: list[str], user_id: int, pagination: PagePagination) -> dict:
        filters: dict = dict(booking__user_id=user_id)
        if statuses:
            filters.update(status__in=statuses)

        q_filters = [
            self.meeting_repo.q_builder(
                or_filters=[dict(booking__user_id=user_id), dict(booking__agent_id=user_id)]
            )
        ]

        meetings: list[Meeting] = await self.meeting_repo.list(
            filters=filters,
            q_filters=q_filters,
            start=pagination.start,
            end=pagination.end,
            related_fields=["booking"],
            ordering="date",
        )

        counted = await self.meeting_repo.list(
            filters=filters,
            q_filters=q_filters,
        ).count()

        data: dict = dict(
            count=counted,
            result=meetings,
            page_info=pagination(count=counted)
        )
        return data
