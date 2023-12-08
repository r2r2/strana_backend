import pytest
from importlib import import_module

from src.news.repos import NewsRepo, NewsUserRoleThrough, NewsTagRepo


@pytest.fixture(scope="function")
def news_tags_repo() -> NewsTagRepo:
    news_tags_repo: NewsTagRepo = getattr(import_module("src.news.repos"), "NewsTagRepo")()
    return news_tags_repo


@pytest.fixture(scope="function")
def news_repo() -> NewsRepo:
    news_repo: NewsRepo = getattr(import_module("src.news.repos"), "NewsRepo")()
    return news_repo


@pytest.fixture(scope="function")
def news_user_role_repo() -> NewsUserRoleThrough:
    news_user_role_repo: NewsUserRoleThrough = getattr(import_module("src.news.repos"), "NewsUserRoleThrough")()
    return news_user_role_repo


@pytest.fixture(scope="function")
async def news_tags_fixture(news_tags_repo) -> None:
    tag_data: dict = dict(
        label="Тег 1",
        slug="tag_1",
        priority=3,
        is_active=True,
    )
    await news_tags_repo.create(data=tag_data)

    tag_data: dict = dict(
        label="Тег 2",
        slug="tag_2",
        priority=2,
        is_active=False,
    )
    await news_tags_repo.create(data=tag_data)

    tag_data: dict = dict(
        label="Тег 3",
        slug="tag_3",
        priority=1,
        is_active=True,
    )
    await news_tags_repo.create(data=tag_data)


@pytest.fixture(scope="function")
async def news_fixture(news_repo, news_user_role_repo, agent_role) -> None:
    from datetime import datetime, timedelta
    from pytz import UTC

    news_data: dict = dict(
        title="Новость 1",
        slug="news_1",
        pub_date=datetime.now(tz=UTC) - timedelta(hours=72),
        is_active=True,
    )
    news_1 = await news_repo.create(data=news_data)
    await news_1.roles.add(agent_role)

    news_data: dict = dict(
        title="Новость 2",
        slug="news_2",
        pub_date=datetime.now(tz=UTC) - timedelta(hours=48),
        is_active=False,
    )
    news_2 = await news_repo.create(data=news_data)
    await news_2.roles.add(agent_role)

    news_data: dict = dict(
        title="Новость 3",
        slug="news_3",
        pub_date=datetime.now(tz=UTC) - timedelta(hours=24),
        is_active=True,
    )
    news_3 = await news_repo.create(data=news_data)
    await news_3.roles.add(agent_role)
