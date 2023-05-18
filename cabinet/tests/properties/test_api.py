import pytest

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


class TestListPropertyTypesEndpoint:
    async def test_property_types_success(self, async_client):
        res = await async_client.get("/properties/types")
        assert res.status_code == 200
        assert res.json() == [
            {"label": "Квартира", "value": "FLAT"},
            {"label": "Паркинг", "value": "PARKING"},
            {"label": "Коммерция", "value": "COMMERCIAL"},
            {"label": "Кладовка", "value": "PANTRY"},
            {"label": "Апартаменты коммерции", "value": "COMMERCIAL_APARTMENT"},
        ]


class TestPropertyBindApi:
    async def test_bind_property_bind_422(self, async_client, property_repo):
        response = await async_client.patch("/properties/bind")
        assert response.status_code == 422
