from http import HTTPStatus

import pytest
from unittest.mock import AsyncMock, patch


from common.depreg.dto import DepregParticipantsDTO, DepregParticipantDTO


pytestmark = pytest.mark.asyncio


class TestUpdateEventParticipantList:

    @pytest.mark.parametrize(
        "phone, code, expected_code",
        [
            ("+79296010011", "ABC", "ABC"),  # update
            ("+79771112233", "CDE", "CDE"),  # create
        ],
    )
    async def test_event_participant_list_case_update(
        self,
        async_client,
        event_list,
        event_participant_list_repo,
        phone,
        code,
        expected_code,
    ):
        get_participants: str = (
            "src.events_list.use_cases.event_participant_list_case.EventParticipantListCase.get_participants"
        )
        get_timeslot: str = (
            "src.events_list.use_cases.event_participant_list_case.EventParticipantListCase.get_timeslots"
        )
        with patch(get_participants, new_callable=AsyncMock) as mock_get_participants:
            with patch(get_timeslot, new_callable=AsyncMock) as mock_get_timeslots:
                mock_get_participants.return_value = DepregParticipantsDTO(
                    data=[DepregParticipantDTO(
                        phone=phone,
                        code=code,
                        eventId=event_list.id,
                        groupId=1,
                    )]
                )
                mock_get_timeslots.return_value = {1: "14:00-15:00"}

                response = await async_client.patch(
                    f"events_list/{event_list.event_id}/update_event_participant_list/",
                )
                assert response.status_code == HTTPStatus.OK

                participant = await event_participant_list_repo.retrieve(filters={"phone": phone})
                assert participant.code == expected_code
