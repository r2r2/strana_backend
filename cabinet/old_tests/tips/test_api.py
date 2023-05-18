from pytest import mark


@mark.asyncio
class TestTipListView(object):
    async def test_success(self, client, tip):
        response = await client.get("/tips")
        response_json = response.json()
        response_count = response_json["count"]
        response_status = response.status_code

        awaitable_count = 1
        awaitable_status = 200

        assert response_count == awaitable_count
        assert response_status == awaitable_status
