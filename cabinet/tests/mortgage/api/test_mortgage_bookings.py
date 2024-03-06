from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


class TestGetMortgageBookings:

    @pytest.mark.skip(reason="Deprecated. Endpoint was moved to calculator service.")
    async def test_get_mortgage_bookings(
        self,
        async_client,
        user_authorization,
    ):
        headers = {"Authorization": user_authorization}
        response = await async_client.get(
            "mortgage/bookings",
            headers=headers,
        )
        assert response.status_code == HTTPStatus.OK
