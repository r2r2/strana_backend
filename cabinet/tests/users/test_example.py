from pytest import mark


@mark.asyncio
class TestTipsExampleCase:

    async def test_tips_create(self, fake_tip, tips_repo):

        tip_created = await tips_repo.create(data=fake_tip)

        assert tip_created.title == fake_tip.get("title")
        assert tip_created.text == fake_tip.get("text")
        assert tip_created.order == int(fake_tip.get("order"))

    def test_tips_sync_api_example(self, fake_tip, sync_client):
        response = sync_client.get("tips")

        assert response.status_code == 200


    async def test_tips_async_api_example(self, async_client):
        response = await async_client.get("tips")

        assert response.status_code == 200
