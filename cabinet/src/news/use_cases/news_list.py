import datetime
from typing import Any, Optional

from common import paginations
from src.users.repos import UserRepo, User
from src.users.exceptions import UserHasNoRoleError

from ..entities import BaseNewsCase
from ..repos import NewsRepo, News, NewsViewedInfoRepo, NewsTagRepo, NewsSettingsRepo, NewsSettings


class NewsListCase(BaseNewsCase):
    """
    Кейс для списка новостей.
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
        user_id: int,
        pagination: paginations.PagePagination,
        tags: list[str],
        project: Optional[str] = None,
        city: Optional[str] = None,
        date_start: Optional[datetime.datetime] = None,
        date_end: Optional[datetime.datetime] = None,
    ) -> dict[str, Any]:
        user: User = await self.user_repo.retrieve(filters=dict(id=user_id), related_fields=["role"])
        if not user.role:
            raise UserHasNoRoleError

        filters = self.get_filters(
            project=project,
            city=city,
            tags=tags,
            user_role=user.role.slug,
            date_start=date_start,
            date_end=date_end,
        )
        annotations = self.get_annotations(user=user)

        news_list: list[News] = await self.news_repo.list(
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
            start=pagination.start,
            end=pagination.end,
            ordering="-pub_date",
        ).distinct()

        # проверяем, что у новостей есть изображения и ставим дефолтные при их отсутствии
        await self.check_images(news_list)

        count: int = len(await self.news_repo.list(filters=filters).distinct())
        news_list_data: dict[str, Any] = dict(count=count, result=news_list, page_info=pagination(count=count))
        return news_list_data

    @staticmethod
    def get_filters(
        tags: list[str],
        project: Optional[str] = None,
        city: Optional[str] = None,
        user_role: Optional[str] = None,
        date_start: Optional[datetime.datetime] = None,
        date_end: Optional[datetime.datetime] = None,
    ) -> dict:
        filters = dict(is_active=True)
        if project:
            filters.update(dict(news_projects__slug=project))
        if city:
            filters.update(dict(news_projects__city__slug=city))
        if tags:
            filters.update(dict(tags__slug__in=tags))
        if user_role:
            filters.update(dict(roles__slug=user_role))

        if date_start and date_end:
            filters.update(dict(pub_date__gte=date_start, pub_date__lte=date_end))
        elif date_start:
            filters.update(dict(pub_date__gte=date_start))
        elif date_end:
            filters.update(dict(pub_date__lte=date_end))

        return filters

    def get_annotations(self, user: User) -> dict:
        user_view_news_qs: Any = self.news_viewed_info_repo.exists(
          filters=dict(
              news_id=self.news_repo.a_builder.build_outer("id"),
              user_id=user.id,
          ),
        )

        annotations: dict[str, Any] = dict(
            is_shown=self.news_repo.a_builder.build_exists(user_view_news_qs),
        )

        return annotations

    async def check_images(self, news_list: list[News]) -> None:
        """
        Метод для подстановки дефолтных картинок.
        """

        news_settings: NewsSettings = await self.news_settings_repo.list().first()
        for news in news_list:
            if not news.image_preview and news_settings:
                news.image_preview = news_settings.default_image_preview
