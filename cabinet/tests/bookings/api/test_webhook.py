import pytest

pytestmark = pytest.mark.asyncio


class TestAmoWebhookApi:
    POST_URL: str = "/booking/amocrm/"
    secret = "secret"

    async def test_amocrm_webhook_view_exist(self, async_client):
        secret = "valid_secret"
        response = await async_client.post(f"{self.POST_URL}{secret}")
        assert response.status_code == 200

        response_data = response.json()
        assert response_data is None

    async def test_amocrm_webhook_view_exist2(self, async_client):
        secret = "valid_secret"

        response = await async_client.post(f"{self.POST_URL}{secret}")
        assert response.status_code == 200

        response_data = response.json()
        assert response_data is None
