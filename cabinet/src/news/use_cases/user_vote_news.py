from typing import Any, Optional

from src.users.repos import UserRepo, User
from src.users.exceptions import UserHasNoRoleError

from ..models import RequestUserVoteNewsModel
from ..entities import BaseNewsCase
from ..repos import NewsRepo, News, NewsViewedInfoRepo, NewsViewedInfo
from ..exceptions import NewsNotFoundError, UserHasNotSeenNewsError, UserAlreadyVoteNewsError


class UserVoteNewsCase(BaseNewsCase):
    """
    Кейс для апи голосования о полезности новости для пользователя.
    """

    def __init__(
        self,
        user_repo: type[UserRepo],
        news_repo: type[NewsRepo],
        news_viewed_info_repo: type[NewsViewedInfoRepo],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.news_repo: NewsRepo = news_repo()
        self.news_viewed_info_repo: NewsViewedInfoRepo = news_viewed_info_repo()

    async def __call__(
        self,
        news_slug: str,
        user_id: int,
        payload: RequestUserVoteNewsModel,
    ) -> None:
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
        )
        if not news:
            raise NewsNotFoundError

        if not news.is_shown:
            raise UserHasNotSeenNewsError

        if news.is_voice_left:
            raise UserAlreadyVoteNewsError

        # добавляем в историю просмотров новости информацию о полезности для пользователя
        news_viewed_info: NewsViewedInfo = await self.news_viewed_info_repo.retrieve(
            filters=dict(id=news.news_viewed_info_id),
        )
        news_viewed_info_data = dict(
            is_voice_left=True,
            is_useful=payload.is_useful,
        )
        await self.news_viewed_info_repo.update(
            model=news_viewed_info,
            data=news_viewed_info_data,
        )

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
        news_viewed_info_id_qs: Any = self.news_viewed_info_repo.retrieve(
            filters=dict(
                news_id=self.news_repo.a_builder.build_outer("id"),
                user_id=user.id,
            ),
        ).values_list("id", flat=True)
        annotations: dict[str, Any] = dict(
            is_shown=self.news_repo.a_builder.build_exists(user_view_news_qs),
            is_voice_left=self.news_repo.a_builder.build_subquery(user_voice_left_news_qs),
            news_viewed_info_id=self.news_repo.a_builder.build_subquery(news_viewed_info_id_qs),
        )

        return annotations
