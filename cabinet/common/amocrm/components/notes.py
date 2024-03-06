from abc import ABC
from datetime import datetime
from typing import Any

import structlog

from common.amocrm.components.interface import AmoCRMInterface
from pytz import UTC

from config.feature_flags import FeatureFlags
from ..constants import AmoEntityTypes, AmoNoteTypes
from ...requests import CommonResponse
from ...unleash.client import UnleashClient


class AmoCRMNotes(AmoCRMInterface, ABC):
    """
    AmoCRM notes integration
    """
    logger = structlog.get_logger(__name__)

    # deprecated
    element_types_mapping: dict[str, int] = {
        "task": 4,
        "lead": 2,
        "contact": 1,
        "company": 3,
        "customer": 12,
    }
    # deprecated
    note_types_mapping: dict[str, int] = {
        "common": 4,
        "call_in": 10,
        "call_out": 11,
        "lead_changed": 3,
        "lead_created": 1,
        "task_result": 13,
        "contact_created": 2,
    }

    # deprecated
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
        print("create_note")
        print(f'{response.data=}')
        print(f'{response.status=}')
        print(f'{response.raw=}')
        if response.data:
            data: list[Any] = response.data["_embedded"]["items"]
        else:
            data: list[Any] = []
        return data
    
    async def create_note_v4(
            self,
            lead_id: int,
            text: str,
            entity_type: str = AmoEntityTypes.LEADS,
            note_type: str = AmoNoteTypes.COMMON,
    ) -> list[Any]:
        """
        Note creation v_4
        https://www.amocrm.ru/developers/content/crm_platform/events-and-notes#notes-add
        """
        route: str = f"/{entity_type}/notes"
        payload: dict[str, Any] = dict(
            add=dict(
                    text=text,
                    entity_id=lead_id,
                    created_at=int(datetime.now(tz=UTC).timestamp()),
                    note_type=note_type,
                )
        )
        response: CommonResponse = await self._request_post_v4(route=route, payload=payload)
        print("create_note_v4")
        print(f'{response.data=}')
        print(f'{response.status=}')
        print(f'{response.raw=}')
        if not response.ok:
            self.logger.info(f"Lead({lead_id}) note sent error: {response.status} with payload data: {payload}.")

        if response.data:
            if "_embedded" in response.data:
                data: list[Any] = response.data["_embedded"]["notes"]
            else:
                # TODO Добавить логирование в сентри
                data: list[Any] = []
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
            self.logger.info(f"Lead note sent: {response.data}")

    async def send_contact_note(
        self,
        contact_id: int,
        message: str,
    ) -> dict:
        """
        Добавление комментария при закреплении клиента
        """
        route: str = f"/contacts/{contact_id}/notes"
        payload = [dict(note_type="common", params=dict(text=message))]
        response: CommonResponse = await self._request_post_v4(route=route, payload=payload)
        if response.data:
            self.logger.info(f"Contact({contact_id}) note sent: {response.data}")
        elif response.errors:
            self.logger.warning(f"Contact({contact_id}) note sent error: {response.status} with payload data {payload}")
        return dict(route=route, status=response.status, request_data=message, data=response.data)

    @property
    def __is_strana_lk_2882_enable(self) -> bool:
        return UnleashClient().is_enabled(FeatureFlags.strana_lk_2882)
