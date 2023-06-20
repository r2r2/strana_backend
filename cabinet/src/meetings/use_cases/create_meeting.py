from typing import Type

from common.amocrm import AmoCRM
from common.amocrm.types import AmoLead
from src.booking.repos import BookingRepo, Booking
from src.booking.constants import BookingSubstages
from src.amocrm.repos import AmocrmStatusRepo, AmocrmStatus
from src.users.repos import UserRepo, User
from src.users.exceptions import UserNotFoundError
from ..constants import MeetingTopicType
from ..repos import Meeting, MeetingRepo
from ..entities import BaseMeetingCase
from ..models import RequestCreateMeetingModel


class CreateMeetingCase(BaseMeetingCase):
    """
    Кейс создания встречи
    """

    lk_client_tag: list[str] = ["ЛК Клиента"]

    def __init__(
            self,
            meeting_repo: Type[MeetingRepo],
            amocrm_class: Type[AmoCRM],
            booking_repo: Type[BookingRepo],
            user_repo: Type[UserRepo],
            amocrm_status_repo: Type[AmocrmStatusRepo]
    ) -> None:
        self.meeting_repo: MeetingRepo = meeting_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.user_repo: UserRepo = user_repo()
        self.amocrm_status_repo: AmocrmStatusRepo = amocrm_status_repo()
        self.amocrm_class: Type[AmoCRM] = amocrm_class

    async def __call__(self, user_id: int, payload: RequestCreateMeetingModel) -> Meeting:
        user: User = await self.user_repo.retrieve(filters=dict(id=user_id))
        if not user:
            raise UserNotFoundError
        property_type: str = payload.property_type

        meeting_data: dict = dict(
            city_id=payload.city_id,
            project_id=payload.project_id,
            type=payload.type,
            topic=MeetingTopicType.BUY,
            date=payload.date,
            property_type=property_type,
        )

        prefetch_fields: list[str] = ["project", "project__city", "city"]
        created_meeting: Meeting = await self.meeting_repo.create(data=meeting_data)
        await created_meeting.fetch_related(*prefetch_fields)

        amo_data: dict = dict(
            tags=self.lk_client_tag,
            property_type=property_type,
            user_amocrm_id=user.amocrm_id,
            contact_ids=[user.amocrm_id],
            creator_user_id=user.id,
            property_id=self.amocrm_class.property_type_field_values.get(property_type).get("enum_id")
        )
        booking_data: dict = dict(
            active=True,
            amocrm_substage=BookingSubstages.MAKE_APPOINTMENT,
        )

        if project := created_meeting.project:
            amocrm_status: AmocrmStatus = await self.amocrm_status_repo.retrieve(
                filters=dict(
                    pipeline_id=project.amo_pipeline_id,
                    name__icontains="Назначить встречу"
                )
            )
            project_data: dict = dict(
                status_id=amocrm_status.id,
                city_slug=project.city.slug,
                project_amocrm_name=project.amocrm_name,
                project_amocrm_enum=project.amocrm_enum,
                project_amocrm_organization=project.amocrm_organization,
                project_amocrm_pipeline_id=project.amo_pipeline_id,
                project_amocrm_responsible_user_id=project.amo_responsible_user_id,
            )
            amo_data.update(project_data)
            booking_data.update(
                project_id=project.id,
                amocrm_status_id=amocrm_status.id,
                amocrm_substage=BookingSubstages.MAKE_APPOINTMENT
            )
        async with await self.amocrm_class() as amocrm:
            lead: list[AmoLead] = await amocrm.create_lead(**amo_data)
            booking_data.update(
                amocrm_id=lead[0].id,
                user_id=user.id,
            )

            amo_notes: str = f"Время встречи: {created_meeting.date.strftime('%Y-%m-%d %H:%M')}"
            await amocrm.send_lead_note(
                lead_id=lead[0].id,
                message=amo_notes,
            )

        booking: Booking = await self.booking_repo.create(data=booking_data)
        await self.meeting_repo.update(model=created_meeting, data=dict(booking_id=booking.id))
        return created_meeting
