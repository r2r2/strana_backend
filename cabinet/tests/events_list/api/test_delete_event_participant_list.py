from datetime import datetime, timedelta
from http import HTTPStatus

import pytest
from pytz import UTC


pytestmark = pytest.mark.asyncio


class TestDeleteEventParticipantList:
    async def test_event_participant_list_case_delete(
        self,
        async_client,
        event_list_repo,
        event_participant_list_repo,
        event_group_repo,
    ):
        today_date: datetime = datetime.now(tz=UTC)
        start_showing_date: datetime = today_date - timedelta(days=1)
        event_list = await event_list_repo.create(
            data=dict(
                name="Test event",
                token="test_token",
                event_date=today_date.strftime("%Y-%m-%d"),
                title="Test title",
                subtitle="Test subtitle",
                event_id=999,
                start_showing_date=start_showing_date.strftime("%Y-%m-%d"),
            )
        )
        await event_participant_list_repo.create(
            data=dict(
                phone="+79296010011",
                code="ABC",
                event=event_list,
                group_id=1,
                timeslot="14:00",
            )
        )
        await event_group_repo.create(
            data=dict(
                event=event_list,
                group_id=1,
                timeslot="14:00",
            )
        )

        response = await async_client.delete(
            f"events_list/{event_list.event_id}/delete_event_participant_list/",
        )
        assert response.status_code == HTTPStatus.OK
        assert await event_participant_list_repo.list(filters={"event": event_list.event_id}) == []
        assert await event_group_repo.list(filters={"event": event_list.event_id}) == []
