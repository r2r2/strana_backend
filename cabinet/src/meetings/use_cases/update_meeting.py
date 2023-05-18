from typing import Type

from ..repos import Meeting, MeetingRepo
from ..entities import BaseMeetingCase
from ..models import RequestUpdateMeetingModel


class UpdateMeetingCase(BaseMeetingCase):
    """
    Кейс изменения встречи
    """
    def __init__(self,meeting_repo: Type[MeetingRepo]) -> None:
        self.meeting_repo: MeetingRepo = meeting_repo()

    async def __call__(self, meeting_id: int, payload: RequestUpdateMeetingModel) -> Meeting:
        update_data: dict = payload.dict(exclude_none=True)

        meeting: Meeting = await self.meeting_repo.retrieve(filters=dict(id=meeting_id))
        update_meeting: Meeting = await self.meeting_repo.update(model=meeting, data=update_data)

        prefetch_fields: list[str] = ["project", "city"]
        await update_meeting.fetch_related(*prefetch_fields)

        return update_meeting
