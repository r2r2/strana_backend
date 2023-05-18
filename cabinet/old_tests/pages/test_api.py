from pytest import mark


@mark.asyncio
class TestBrokerRegistrationRetrieveView(object):
    async def test_success(self, client, broker_registration):
        response = await client.get("/pages/broker_registration")
        response_status = response.status_code

        awaitable_status = 200

        assert response_status == awaitable_status
