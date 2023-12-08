from pytest import mark


@mark.asyncio
class TestNewsTags:

    async def test_news_tags_list_async_api(self, async_client, news_tags_repo, news_tags_fixture):
        # проверка количества добавленных фикстур
        news_tags_count = await news_tags_repo.list().count()
        assert news_tags_count == 3

        response_news_active_tags = await async_client.get("news/tags")

        assert response_news_active_tags.status_code == 200  # общая проверка апи
        assert len(response_news_active_tags.json()) == 2  # проверка фильтрации is_active
        assert response_news_active_tags.json()[0]["slug"] == "tag_3"  # проверка сортировки апи по приоритету


@mark.asyncio
class TestNews:

    async def test_news_list_async_api(self, async_client, agent_authorization, news_repo, news_fixture):
        news_count = await news_repo.list().count()
        assert news_count == 3  # проверка количества добавленных фикстур

        headers = {"Authorization": agent_authorization}
        response_news = await async_client.get("news", headers=headers)

        assert response_news.status_code == 200  # общая проверка апи
        assert len(response_news.json()["result"]) == 2  # проверка фильтрации is_active
        assert response_news.json()["result"][0]["slug"] == "news_3"  # проверка сортировки апи по дате

    async def test_news_detail_async_api(self, async_client, agent_authorization):
        headers = {"Authorization": agent_authorization}
        response_news_1 = await async_client.get("news/news_1", headers=headers)
        response_news_2 = await async_client.get("news/news_2", headers=headers)

        assert response_news_1.status_code == 200  # общая проверка апи (новость доступна)
        assert response_news_2.status_code == 404  # новость не существует

        response_news = await async_client.get("news", headers=headers)  # проверяем просмотренные новости в списке
        assert response_news.json()["result"][0]["isShown"] is False  # проверка is_shown (не просмотрено)
        assert response_news.json()["result"][1]["isShown"] is True  # проверка is_shown (просмотрено)

    async def test_user_vote_news_async_api(self, async_client, agent_authorization):
        headers = {"Authorization": agent_authorization}
        payload = dict(is_useful=True)
        response_news_1 = await async_client.patch(
            "news/news_1/mark_benefit",
            json=payload,
            headers=headers,
        )
        response_news_2 = await async_client.patch(
            "news/news_2/mark_benefit",
            json=payload,
            headers=headers,
        )
        response_news_3 = await async_client.patch(
            "news/news_3/mark_benefit",
            json=payload,
            headers=headers,
        )
        second_response_news_1 = await async_client.patch(
            "news/news_1/mark_benefit",
            json=payload,
            headers=headers,
        )

        assert response_news_1.status_code == 200  # общая проверка апи (голос добавлен)
        assert response_news_2.status_code == 404  # новость не найдена
        assert response_news_3.status_code == 400  # новость не просмотрена
        assert second_response_news_1.status_code == 400  # голос уже оставлен

        response_news_1 = await async_client.get("news/news_1", headers=headers)  # значение голоса смотри в деталке
        assert response_news_1.json()["isUseful"] is True  # проверка is_useful (значение голоса)
