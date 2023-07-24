from pytest import mark


@mark.asyncio
class TestEvents:

    async def test_event_list_async_api_example(self, async_client, event_repo, agent_authorization, event_fixture):
        headers = {"Authorization": agent_authorization}
        event_count = await event_repo.list().count()

        response = await async_client.get("events", headers=headers)

        assert response.status_code == 200
        assert event_count == 3
        assert len(response.json()["result"]) == 2

    async def test_event_detail_async_api_example(self, async_client, event_repo, agent_authorization, event_fixture):
        headers = {"Authorization": agent_authorization}\

        response_event_1 = await async_client.get("events/1", headers=headers)
        response_event_2 = await async_client.get("events/2", headers=headers)
        response_event_3 = await async_client.get("events/3", headers=headers)

        assert response_event_1.status_code == 200
        assert response_event_2.status_code == 200
        assert response_event_3.status_code == 400
        assert response_event_1.json() and response_event_2.json()

    async def test_event_record_async_api_example(self, async_client, event_repo, agent_authorization, event_fixture):
        headers = {"Authorization": agent_authorization}
        params = {"showOnlyRecordedMeetings": "true"}

        record_response_event_1 = await async_client.patch("events/1/accept", headers=headers)
        record_response_event_2 = await async_client.patch("events/2/accept", headers=headers)
        record_response_event_3 = await async_client.patch("events/3/accept", headers=headers)
        record_list_response = await async_client.get("events", headers=headers, params=params)

        assert record_response_event_1.status_code == 200
        assert record_response_event_2.status_code == 400
        assert record_response_event_3.status_code == 400
        assert len(record_list_response.json()["result"]) == 1

    async def test_event_refuse_async_api_example(self, async_client, event_repo, agent_authorization, event_fixture):
        headers = {"Authorization": agent_authorization}

        await async_client.patch("events/1/accept", headers=headers)
        response = await async_client.patch("events/1/refuse", headers=headers)

        assert response.status_code == 200
