from datetime import datetime
from typing import Any, Optional

from common import dependencies, paginations
from fastapi import APIRouter, Depends, Query, status, Path, Body

from src.users.repos import UserRepo

from ..models import NewsTagModel, ResponseNewsListModel, ResponseDetailNewsModel, RequestUserVoteNewsModel
from ..repos import NewsRepo, NewsViewedInfoRepo, NewsTagRepo, NewsSettingsRepo
from ..use_cases import NewsTagListCase, NewsListCase, NewsDetailCase, UserVoteNewsCase

router = APIRouter(prefix="/news", tags=["news"])


@router.get(
    "/tags",
    status_code=status.HTTP_200_OK,
    response_model=list[NewsTagModel],
)
async def news_tags_list_view():
    """
    Апи списка тегов новостей.
    """

    resources: dict[str, Any] = dict(news_tag_repo=NewsTagRepo)
    news_tags_list_case: NewsTagListCase = NewsTagListCase(**resources)
    return await news_tags_list_case()


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ResponseNewsListModel,
)
async def news_list_view(
    pagination: paginations.PagePagination = Depends(dependencies.Pagination()),
    project: str = Query(
        default=None,
        description="Фильтр по проектам",
    ),
    city: str = Query(
        default=None,
        description="Фильтр по городам",
    ),
    tags: list[str] = Query(
        default=[],
        description="Фильтр по тегам",
    ),
    date_start: Optional[datetime] = Query(
        default=None,
        description="Дата начала фильтрации по дате публикации",
        alias="dateStart",
    ),
    date_end: Optional[datetime] = Query(
        default=None,
        description="Дата окончания фильтрации по дате публикации",
        alias="dateEnd",
    ),
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
):
    """
    Апи списка новостей.
    """

    resources: dict[str, Any] = dict(
        user_repo=UserRepo,
        news_repo=NewsRepo,
        news_viewed_info_repo=NewsViewedInfoRepo,
        news_tag_repo=NewsTagRepo,
        news_settings_repo=NewsSettingsRepo,
    )
    news_list_case: NewsListCase = NewsListCase(**resources)
    return await news_list_case(
        user_id=user_id,
        pagination=pagination,
        project=project,
        city=city,
        tags=tags,
        date_start=date_start,
        date_end=date_end,
    )


@router.get(
    "/{news_slug}",
    status_code=status.HTTP_200_OK,
    response_model=ResponseDetailNewsModel,
)
async def news_detail_view(
    news_slug: str = Path(...),
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
):
    """
    Апи деталки новостей.
    """

    resources: dict[str, Any] = dict(
        user_repo=UserRepo,
        news_repo=NewsRepo,
        news_viewed_info_repo=NewsViewedInfoRepo,
        news_tag_repo=NewsTagRepo,
        news_settings_repo=NewsSettingsRepo,
    )
    news_detail_case: NewsDetailCase = NewsDetailCase(**resources)
    return await news_detail_case(
        news_slug=news_slug,
        user_id=user_id,
    )


@router.patch(
    "/{news_slug}/mark_benefit",
    status_code=status.HTTP_200_OK,
)
async def user_vote_news_view(
    news_slug: str = Path(...),
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
    payload: RequestUserVoteNewsModel = Body(...),
):
    """
    Апи голосования о полезности новости для пользователя.
    """

    resources: dict[str, Any] = dict(
        user_repo=UserRepo,
        news_repo=NewsRepo,
        news_viewed_info_repo=NewsViewedInfoRepo,
    )
    user_vote_news_case: UserVoteNewsCase = UserVoteNewsCase(**resources)
    return await user_vote_news_case(
        news_slug=news_slug,
        user_id=user_id,
        payload=payload,
    )
