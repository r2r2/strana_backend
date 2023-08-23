from datetime import datetime, timedelta

from common.amocrm import AmoCRM
from src.booking.types import WebhookLead
from ..entities import BaseMeetingService
from ..repos import MeetingRepo, Meeting


class ImportMeetingFromAmoService(BaseMeetingService):
    """
    Импорт данных встречи из АМО (пока только дата)
    """
    def __init__(
            self,
            meeting_repo: type[MeetingRepo],
            amocrm_class: type[AmoCRM],
    ) -> None:
        self.meeting_repo: MeetingRepo = meeting_repo()
        self.amocrm_class: type[AmoCRM] = amocrm_class

    async def __call__(self, webhook_lead: WebhookLead) -> None:
        meeting: Meeting = await self.meeting_repo.retrieve(filters=dict(booking__amocrm_id=webhook_lead.lead_id))
        if meeting:
            data_from_amo: dict = self._parse_meeting_data(webhook_lead=webhook_lead)
            data_for_update: dict = dict(
                date=self._parse_date_from_amo(data_from_amo=data_from_amo),
                meeting_link=data_from_amo.get("meeting_link"),
            )
            await self.meeting_repo.update(model=meeting, data=data_for_update)

    def _parse_meeting_data(self, webhook_lead: WebhookLead) -> dict:
        """
        Парсинг данных из АМО
        """
        parsed_data: dict = dict()
        if date_next_contact_custom_value := webhook_lead.custom_fields.get(
            self.amocrm_class.meeting_date_next_contact_field_id
        ):
            next_contact_timestamp_value: float = date_next_contact_custom_value.value
            parsed_data["next_contact_timestamp_value"] = next_contact_timestamp_value
        if zoom_timestamp_custom_value := webhook_lead.custom_fields.get(
            self.amocrm_class.meeting_date_zoom_field_id
        ):
            zoom_timestamp_value: float = zoom_timestamp_custom_value.value
            parsed_data["zoom_timestamp_value"] = zoom_timestamp_value
        if sensei_timestamp_custom_value := webhook_lead.custom_fields.get(
            self.amocrm_class.meeting_date_sensei_field_id
        ):
            sensei_timestamp_value: float = sensei_timestamp_custom_value.value
            parsed_data["sensei_timestamp_value"] = sensei_timestamp_value
        if meeting_link_custom_value := webhook_lead.custom_fields.get(
            self.amocrm_class.meeting_link_field_id
        ):
            meeting_link: str = meeting_link_custom_value.value
            parsed_data["meeting_link"] = meeting_link

        return parsed_data

    def _parse_date_from_amo(self, data_from_amo: dict) -> datetime:
        return datetime.fromtimestamp(
            int(
                data_from_amo.get("next_contact_timestamp_value") or
                data_from_amo.get("zoom_timestamp_value") or
                data_from_amo.get("sensei_timestamp_value")
            )
        ).replace(tzinfo=None) + timedelta(hours=2)
