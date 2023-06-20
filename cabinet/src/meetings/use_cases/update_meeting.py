from typing import Any, Type

from common.amocrm import AmoCRM
from src.amocrm.repos import AmocrmStatus, AmocrmStatusRepo
from src.booking.repos import BookingRepo
from src.booking.constants import BookingSubstages

from ..constants import MeetingStatus
from ..entities import BaseMeetingCase
from ..models import RequestUpdateMeetingModel
from ..repos import Meeting, MeetingRepo


class UpdateMeetingCase(BaseMeetingCase):
    """
    Кейс изменения встречи
    """
    def __init__(
        self,
        meeting_repo: Type[MeetingRepo],
        booking_repo: Type[BookingRepo],
        amocrm_class: Type[AmoCRM],
        amocrm_status_repo: Type[AmocrmStatusRepo],
    ) -> None:
        self.meeting_repo: MeetingRepo = meeting_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.amocrm_class: Type[AmoCRM] = amocrm_class

    async def __call__(self, meeting_id: int, payload: RequestUpdateMeetingModel) -> Meeting:
        update_data: dict = payload.dict(exclude_none=True)
        update_data.update(status=MeetingStatus.NOT_CONFIRM)

        meeting: Meeting = await self.meeting_repo.retrieve(
            filters=dict(id=meeting_id),
            related_fields=["booking", "project"],
        )
        update_meeting: Meeting = await self.meeting_repo.update(model=meeting, data=update_data)
        prefetch_fields: list[str] = ["project", "project__city", "city"]
        await update_meeting.fetch_related(*prefetch_fields)

        amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
            filters=dict(
                pipeline_id=meeting.project.amo_pipeline_id,
                name__icontains="Назначить встречу"
            )
        )
        booking_data: dict = dict(
            amocrm_status_id=amocrm_status.id,
            amocrm_substage=BookingSubstages.MAKE_APPOINTMENT,
        )
        await self.booking_repo.update(model=meeting.booking, data=booking_data)

        async with await self.amocrm_class() as amocrm:
            lead_options: dict[str, Any] = dict(
                lead_id=meeting.booking.amocrm_id,
                status_id=amocrm_status.id,
            )
            await amocrm.update_lead(**lead_options)

            amo_notes: str = f"Новое время встречи: {update_meeting.date.strftime('%Y-%m-%d %H:%M')}"
            await amocrm.send_lead_note(
                lead_id=update_meeting.booking.amocrm_id,
                message=amo_notes,
            )

        return update_meeting
