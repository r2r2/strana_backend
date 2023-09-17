import pytest

from fastapi import status

pytestmark = pytest.mark.asyncio


class TestFavouritesApi:
    POST_URL: str = "/booking/create_booking"

    async def test_create_booking_view_401(self, async_client, property_repo, user_authorization):
        headers: dict = dict()
        response = await async_client.post(self.POST_URL, headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_booking_view_422(self, async_client, user_authorization):
        headers: dict = {"Authorization": user_authorization}
        data: dict = dict()
        response = await async_client.post(self.POST_URL, headers=headers, json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
