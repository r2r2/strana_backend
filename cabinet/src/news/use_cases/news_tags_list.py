from ..entities import BaseNewsCase
from ..repos import NewsTagRepo, NewsTag


class NewsTagListCase(BaseNewsCase):
    """
    Кейс для списка тегов новостей.
    """

    def __init__(
        self,
        news_tag_repo: type[NewsTagRepo],
    ) -> None:
        self.news_tag_repo: NewsTagRepo = news_tag_repo()

    async def __call__(self) -> list[NewsTag]:
        news_tags: list[NewsTag] = await self.news_tag_repo.list(
            filters=dict(is_active=True),
            ordering="priority",
        )

        return news_tags
