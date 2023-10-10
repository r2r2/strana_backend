from http import HTTPStatus

import pytest
from unittest.mock import AsyncMock, patch


from common.depreg.dto import DepregParticipantsDTO, DepregParticipantDTO


pytestmark = pytest.mark.asyncio


class TestUpdateEventParticipantList:

    @pytest.fixture(scope="function")
    async def event_list(self, event_list_repo):
        event_list = await event_list_repo.create(
            data=dict(
                name="Test event",
                token="test_token",
                event_date="2023-01-01 00:00:00",
                title="Test title",
                subtitle="Test subtitle",
            )
        )
        return event_list

    @pytest.fixture(scope="function")
    async def event_participant_list(self, event_participant_list_repo, event_list):
        event_participant_list = await event_participant_list_repo.create(
            data=dict(
                phone="+79992223344",
                code="test_code",
                event=event_list,
            )
        )
        return event_participant_list

    @pytest.mark.parametrize(
        "phone, code, expected_code",
        [
            ("+79992223344", "ABC", "ABC"),  # update
            ("+79771112233", "CDE", "CDE"),  # create
        ],
    )
    async def test_event_participant_list_case_update(
        self,
        async_client,
        event_list,
        event_participant_list,
        event_participant_list_repo,
        phone,
        code,
        expected_code,
    ):
        with patch(
            "src.events_list.use_cases.event_participant_list_case.EventParticipantListCase.get_participants",
            new_callable=AsyncMock,
        ) as mock_get_participants:
            mock_get_participants.return_value = DepregParticipantsDTO(
                data=[DepregParticipantDTO(phone=phone, code=code, eventId=event_list.id)]
            )
            response = await async_client.patch(
                f"events_list/{event_list.id}/update_event_participant_list/",
            )
            assert response.status_code == HTTPStatus.OK

            participant = await event_participant_list_repo.retrieve(filters={"phone": phone})
            assert participant.code == expected_code
