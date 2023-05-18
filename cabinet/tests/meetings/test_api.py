import pytest
from datetime import datetime

from pydantic import ValidationError

from src.meetings import exceptions

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


class TestMeetingsList:
    #Todo для теста успеха нужны фикстуры других сущностей
    date_fixture: datetime = datetime.now()
    status_fixture: str = "not_confirm"
    async def test_create_meeting(self, meeting_repo):
        meeting_data: dict = dict(date=self.date_fixture, status=self.status_fixture)
        meeting = await meeting_repo.create(data=meeting_data)
        assert meeting.status == self.status_fixture

    async def test_meeting_list_not_found(self, async_client, meeting_fixture):
        with pytest.raises(ValidationError) as error:
            await async_client.get("/meetings", params=dict(status=['not_confirm']))
