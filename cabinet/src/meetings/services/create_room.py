from typing import Type

from common.amocrm import AmoCRM
from common.kontur_talk.kontur_talk import KonturTalkAPI

from ..repos import Meeting, MeetingRepo
from ..entities import BaseMeetingService


class CreateRoomService(BaseMeetingService):
    def __init__(
        self,
        kounter_talk_api: Type[KonturTalkAPI],
        meeting_repo: Type[MeetingRepo],
        amocrm_class: Type[AmoCRM],
    ):
        self.kontur_talk_api = kounter_talk_api
        self.meeting_repo: MeetingRepo = meeting_repo()
        self.amocrm_class = amocrm_class

    async def __call__(self, unix_datetime: float, meeting_id: int):
        room_name = f"{unix_datetime + meeting_id}"
        room_link = await self.kontur_talk_api.create_room(room_name=room_name, meeting_id=meeting_id)

        meeting: Meeting = await self.meeting_repo.retrieve(
            filters=dict(id=meeting_id),
            related_fields=["booking"],
        )
        await self.meeting_repo.update(model=meeting, data=dict(meeting_link=room_link))

        amo_notes: str = f"Ссылка на встречу: {room_link}"
        async with await self.amocrm_class() as amocrm:
            await amocrm.send_lead_note(
                lead_id=meeting.booking.amocrm_id,
                message=amo_notes,
            )

        await KonturTalkAPI().open_room(room_name)
