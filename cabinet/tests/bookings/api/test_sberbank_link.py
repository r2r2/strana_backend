import pytest
from fastapi import status

pytestmark = pytest.mark.asyncio


class TestSberbankLinkApi:
    async def test_sberbank_link_401(
            self,
            async_client,
            booking,
    ):
        response = await async_client.post(
            f"/booking/sberbank_link/{booking.id}"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_sberbank_link_422(self, async_client, user_authorization, booking):
        headers: dict = {"Authorization": user_authorization}
        data: dict = dict()
        response = await async_client.post(f"/booking/sberbank_link/{booking.id}", headers=headers, json=data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.text == '{"detail":[{"loc":["body","payment_page_view"],"msg":"field required","type":"value_error.missing"}]}'

    @pytest.mark.parametrize("payment_page_view", ["WRONG_VALUE"])
    async def test_sberbank_link_payment_page_view_422(
            self, async_client, user_authorization, booking, payment_page_view
    ):
        headers: dict = {"Authorization": user_authorization}
        data: dict = dict(payment_page_view=payment_page_view)
        response = await async_client.post(f"/booking/sberbank_link/{booking.id}", headers=headers, json=data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
