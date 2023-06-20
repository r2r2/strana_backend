from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


class TestCreateTicket:

    async def test_create_ticket(
        self,
        async_client,
        user_authorization,
        city_repo,
    ):
        await city_repo.create({"slug": "spb", "name": "Санкт-Петербург"})
        headers = {"Authorization": user_authorization}
        test_payload = dict(
            name="test",
            phone="+79999999999",
            user_amocrm_id=1,
            booking_amocrm_id=1,
            note="test",
            type="test",
            city="spb",
        )
        response = await async_client.post(
            "users/ticket",
            headers=headers,
            json=test_payload,
        )
        assert response.status_code == HTTPStatus.CREATED
