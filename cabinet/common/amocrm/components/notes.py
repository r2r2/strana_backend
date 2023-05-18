from abc import ABC
from datetime import datetime
from typing import Any

from common.amocrm.components.interface import AmoCRMInterface
from pytz import UTC

from ...requests import CommonResponse


class AmoCRMNotes(AmoCRMInterface, ABC):
    """
    AmoCRM notes integration
    """

    element_types_mapping: dict[str, int] = {
        "task": 4,
        "lead": 2,
        "contact": 1,
        "company": 3,
        "customer": 12,
    }
    note_types_mapping: dict[str, int] = {
        "common": 4,
        "call_in": 10,
        "call_out": 11,
        "lead_changed": 3,
        "lead_created": 1,
        "task_result": 13,
        "contact_created": 2,
    }

    async def create_note(self, lead_id: int, text: str, element: str, note: str) -> list[Any]:
        """
        Note creation
        """
        route: str = "/notes"
        payload: dict[str, Any] = dict(
            add=[
                dict(
                    text=text,
                    element_id=lead_id,
                    created_at=int(datetime.now(tz=UTC).timestamp()),
                    note_type=self.note_types_mapping.get(note),
                    element_type=self.element_types_mapping.get(element),
                )
            ]
        )
        response: CommonResponse = await self._request_post(route=route, payload=payload)
        if response.data:
            data: list[Any] = response.data["_embedded"]["items"]
        else:
            data: list[Any] = []
        return data

    async def send_lead_note(
        self,
        lead_id: int,
        message: str,
    ):
        """
        Добавление системного примечания к сделке
        """
        route: str = f"/leads/{lead_id}/notes"
        payload = [dict(note_type="common", params=dict(text=message))]
        response: CommonResponse = await self._request_post_v4(route=route, payload=payload)
        if response.data:
            data: list[Any] = response.data["_embedded"]["notes"]
        else:
            data: list[Any] = []
        return data

    async def send_contact_note(
        self,
        contact_id: int,
        message: str,
    ):
        """
        Добавление комментария при закреплении клиента
        """
        route: str = f"/contacts/{contact_id}/notes"
        payload = [dict(note_type="common", params=dict(text=message))]
        response: CommonResponse = await self._request_post_v4(route=route, payload=payload)
        if response.data:
            data: list[Any] = response.data["_embedded"]["notes"]
        else:
            data: list[Any] = []
        return data