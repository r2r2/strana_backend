import pytest
from starlette import status

pytestmark = pytest.mark.asyncio


class TestFAQList:
    async def test_get_faq_empty_list(self, async_client):
        response = await async_client.get("faq")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "count": 0,
            "result": []
        }

    async def test_get_faq_list(self, async_client, faq_list):
        response = await async_client.get("faq")
        assert response.status_code == status.HTTP_200_OK

        res_json = response.json()
        assert res_json["count"] == 10  # в фикстуре создаётся 10 записей
        for faq in res_json["result"]:
            assert isinstance(faq["id"], int)
            assert isinstance(faq["slug"], str)
            assert isinstance(faq["isActive"], bool)
            assert isinstance(faq["order"], int)
            assert isinstance(faq["question"], str)
            assert isinstance(faq["answer"], str)

    async def test_get_faq_list_active_only(self, async_client, faq_list, faq_repo):
        """Проверяем, что на фронт уходят только is_active=True"""

        #  Добавляем неактивный
        await faq_repo.create(
            {
                "slug": "inactive",
                "is_active": False,
                "question": "some question",
                "answer": "some answer",
            }
        )

        response = await async_client.get("faq")
        assert response.status_code == status.HTTP_200_OK

        res_json = response.json()
        for faq in res_json["result"]:
            assert faq["isActive"] is True
