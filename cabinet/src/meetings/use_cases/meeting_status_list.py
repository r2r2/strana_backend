from typing import Type

from ..entities import BaseMeetingCase
from ..repos import MeetingStatus, MeetingStatusRepo


class MeetingsStatusListCase(BaseMeetingCase):
    """
    Кейс получения списка статусов мероприятий.
    """

    def __init__(
        self,
        status_meeting_repo: Type[MeetingStatusRepo],
    ) -> None:
        self.status_meeting_repo: MeetingStatusRepo = status_meeting_repo()

    async def __call__(self) -> list[MeetingStatus]:
        meeting_statuses: list[MeetingStatus] = await self.status_meeting_repo.list()
        return meeting_statuses
