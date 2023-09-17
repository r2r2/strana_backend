import pytest

from fastapi import status

pytestmark = pytest.mark.asyncio


class TestFavouritesApi:
    POST_URL: str = "/favourites/latest"
    GET_URL: str = "/favourites/latest"
    GET_IDS_URL: str = "/favourites/latest/ids"

    async def test_favourites_viewed_401(self, async_client, property_repo, user_authorization):
        headers: dict = dict()
        response = await async_client.post(self.POST_URL, headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_favourites_viewed_422(self, async_client, property_repo, user_authorization):
        headers: dict = {"Authorization": user_authorization}
        response = await async_client.post(self.POST_URL, headers=headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # async def test_favourites_viewed_201(self, async_client, property_repo, user_authorization, property):
    #     headers: dict = {"Authorization": user_authorization}
    #     favorites_data: list[str] = [property.global_id]
    #     response = await async_client.post(self.POST_URL, headers=headers, json=favorites_data)
    #     result: list[dict] = response.json()
    #     assert result[0].get("propertyId") == property.id
    #     assert response.status_code == status.HTTP_201_CREATED

    # async def test_favourites_viewed_404(self, async_client, property_repo, user_authorization, property):
    #     headers: dict = {"Authorization": user_authorization}
    #     favorites_data: list[str] = [property.global_id + "salt"]
    #     response = await async_client.post(self.POST_URL, headers=headers, json=favorites_data)
    #     assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_viewed_properties_list_view_401(self, async_client, property_repo, user_authorization):
        headers: dict = dict()
        response = await async_client.get(self.GET_URL, headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_viewed_properties_list_view_200(self, async_client, user_authorization):
        headers: dict = {"Authorization": user_authorization}
        response = await async_client.get(self.GET_URL, headers=headers)
        assert response.status_code == status.HTTP_200_OK

    async def test_viewed_properties_list_ids_401(self, async_client, property_repo, user_authorization):
        headers: dict = dict()
        response = await async_client.get(self.GET_IDS_URL, headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_viewed_properties_list_ids_200(self, async_client, user_authorization):
        headers: dict = {"Authorization": user_authorization}
        response = await async_client.get(self.GET_IDS_URL, headers=headers)
        assert response.status_code == status.HTTP_200_OK
