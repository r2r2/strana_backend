from typing import Any, Optional

from src.users.repos import UserRepo, User
from src.users.exceptions import UserHasNoRoleError

from ..entities import BaseNewsCase
from ..repos import NewsRepo, News, NewsViewedInfoRepo, NewsTagRepo, NewsSettingsRepo, NewsSettings
from ..exceptions import NewsNotFoundError


class NewsDetailCase(BaseNewsCase):
    """
    Кейс для деталки новостей.
    """

    def __init__(
        self,
        user_repo: type[UserRepo],
        news_repo: type[NewsRepo],
        news_viewed_info_repo: type[NewsViewedInfoRepo],
        news_tag_repo: type[NewsTagRepo],
        news_settings_repo: type[NewsSettingsRepo],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.news_repo: NewsRepo = news_repo()
        self.news_viewed_info_repo: NewsViewedInfoRepo = news_viewed_info_repo()
        self.news_tag_repo: NewsTagRepo = news_tag_repo()
        self.news_settings_repo: NewsSettingsRepo = news_settings_repo()

    async def __call__(
        self,
        news_slug: str,
        user_id: int,
    ) -> News:
        user: User = await self.user_repo.retrieve(filters=dict(id=user_id), related_fields=["role"])
        if not user.role:
            raise UserHasNoRoleError

        filters = dict(
            is_active=True,
            slug=news_slug,
            roles__slug=user.role.slug,
        )
        annotations = self.get_annotations(user=user)

        news: Optional[News] = await self.news_repo.retrieve(
            filters=filters,
            annotations=annotations,
            prefetch_fields=[
                "roles",
                "news_projects",
                "news_projects__city",
                dict(
                    relation="tags",
                    queryset=self.news_tag_repo.list(filters=dict(is_active=True)),
                    to_attr="active_tags",
                ),
            ],
        )
        if not news:
            raise NewsNotFoundError

        # добавляем в историю информацию о просмотре пользователем новости
        if not news.is_shown:
            news_viewed_info_data = dict(news_id=news.id, user_id=user.id)
            await self.news_viewed_info_repo.create(data=news_viewed_info_data)

            # добавляем поля, которые не были с аннотированы ранее, так как не было просмотра новости в истории
            news.is_voice_left = False
            news.is_useful = False

        # проверяем, что у новости есть изображение и ставим дефолтные при его отсутствии
        await self.check_images(news)

        return news

    def get_annotations(self, user: User) -> dict:
        user_view_news_qs: Any = self.news_viewed_info_repo.exists(
            filters=dict(
                news_id=self.news_repo.a_builder.build_outer("id"),
                user_id=user.id,
            ),
        )
        user_voice_left_news_qs: Any = self.news_viewed_info_repo.retrieve(
            filters=dict(
                news_id=self.news_repo.a_builder.build_outer("id"),
                user_id=user.id,
            ),
        ).values_list("is_voice_left", flat=True)
        user_voted_result_news_qs: Any = self.news_viewed_info_repo.retrieve(
            filters=dict(
                news_id=self.news_repo.a_builder.build_outer("id"),
                user_id=user.id,
            ),
        ).values_list("is_useful", flat=True)

        annotations: dict[str, Any] = dict(
            is_shown=self.news_repo.a_builder.build_exists(user_view_news_qs),
            is_voice_left=self.news_repo.a_builder.build_subquery(user_voice_left_news_qs),
            is_useful=self.news_repo.a_builder.build_subquery(user_voted_result_news_qs),
        )

        return annotations

    async def check_images(self, news: News) -> None:
        """
        Метод для подстановки дефолтных картинок.
        """

        news_settings: NewsSettings = await self.news_settings_repo.list().first()
        if not news.image and news_settings:
            news.image = news_settings.default_image
