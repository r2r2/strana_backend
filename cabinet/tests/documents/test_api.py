from pytest import mark


@mark.asyncio
class TestInstructions:

    async def test_instruction_by_slug_api(self, async_client, instruction_fixture):
        response = await async_client.get("documents/instructions/slug")

        assert response.status_code == 200
        assert response.json()["slug"] == "slug"
        assert response.json()["label"] == "text"
