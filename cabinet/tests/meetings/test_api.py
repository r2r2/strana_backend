from http import HTTPStatus

import pytest
from datetime import datetime


# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


class TestMeetingsList:
    date_fixture: datetime = datetime.now()

    def mock_deleted_user_check(*args, **kwargs):
        pass

    async def test_create_meeting(self, meeting_repo, meeting_status):
        meeting_data: dict = dict(date=self.date_fixture, status=meeting_status)
        meeting = await meeting_repo.create(data=meeting_data)
        assert meeting.status == meeting_status

    async def test_meeting_list_not_found(self, async_client, monkeypatch, user_authorization):
        monkeypatch.setattr("common.dependencies.users.DeletedUserCheck.__call__", self.mock_deleted_user_check)
        headers = {"Authorization": user_authorization}
        response = await async_client.get("/meetings", params=dict(client_id='not_confirm'), headers=headers)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
