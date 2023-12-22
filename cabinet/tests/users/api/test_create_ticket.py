from http import HTTPStatus
from unittest.mock import AsyncMock, patch

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
            type="test",
            city="spb",
        )
        mock_amocrm: str = "src.dashboard.use_cases.create_ticket.CreateTicketCase.process_amocrm"
        with patch(mock_amocrm, new_callable=AsyncMock):
            response = await async_client.post(
                "users/ticket",
                headers=headers,
                json=test_payload,
            )
            assert response.status_code == HTTPStatus.CREATED
