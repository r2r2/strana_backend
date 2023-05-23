from datetime import datetime, timedelta
from typing import Type

from common.amocrm import AmoCRM
from src.meetings.constants import MeetingType
from src.meetings.entities import BaseMeetingCase
from src.meetings.repos import MeetingRepo, Meeting
from src.meetings.tasks import create_kontur_talk_room_task
from fastapi import status


class ConfirmMeetingCase(BaseMeetingCase):

    def __init__(self, meeting_repo: Type[MeetingRepo]):
        self.meeting_repo: MeetingRepo = meeting_repo()

    async def __call__(
            self,
            meeting_id: int,
            date: datetime,
    ):
        meeting: Meeting = await self.meeting_repo.retrieve(filters=dict(id=meeting_id))

        if not meeting:
            return status.HTTP_200_OK

        if meeting.type == MeetingType.ONLINE:
            create_kontur_talk_room_task.apply_async((date, meeting_id), eta=(date - timedelta(hours=1)))
