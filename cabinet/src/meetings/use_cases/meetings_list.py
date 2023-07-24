from typing import Type

import structlog

from common.paginations import PagePagination
from ..entities import BaseMeetingCase
from ..repos import Meeting, MeetingRepo


class MeetingsListCase(BaseMeetingCase):
    """
    Кейс для списка встреч
    """
    def __init__(
        self,
        meeting_repo: Type[MeetingRepo],
    ) -> None:
        self.meeting_repo: MeetingRepo = meeting_repo()
        self.logger = structlog.getLogger(__name__)

    async def __call__(self, *, statuses: list[str], user_id: int, pagination: PagePagination) -> dict:
        filters: dict = dict(booking__user_id=user_id)
        if statuses:
            self.logger.info(f"Add filter with {statuses=}")
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
