from pytest import mark
from enum import StrEnum

@mark.asyncio
class TestSlider:

    async def test_slider_api(self, async_client, slide):
        response = await async_client.get("dashboard/slides")

        assert response.status_code == 200
        assert type(response.json()) == list
        assert response.json()[0].keys() is not None 