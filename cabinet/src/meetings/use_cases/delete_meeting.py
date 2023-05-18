from typing import Type

from ..exceptions import MeetingNotFoundError
from ..repos import Meeting, MeetingRepo
from ..entities import BaseMeetingCase


class DeleteMeetingCase(BaseMeetingCase):
    """
    Кейс удаления встречи
    """
    def __init__(self,meeting_repo: Type[MeetingRepo]) -> None:
        self.meeting_repo: MeetingRepo = meeting_repo()

    async def __call__(self, meeting_id: int) -> None:
        meeting: Meeting = await self.meeting_repo.retrieve(filters=dict(id=meeting_id))

        if not meeting:
            raise MeetingNotFoundError

        await self.meeting_repo.delete(model=meeting)
