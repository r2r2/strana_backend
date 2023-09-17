from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Path
from src.main_page import models
from src.main_page import repos as main_page_repos
from src.main_page import use_cases

router = APIRouter(prefix="/broker/main_page", tags=["MainPage"])


@router.get(
    "/content/{slug}",
    status_code=HTTPStatus.OK,
    response_model=list[models.MainPageContentDetailResponse],
)
async def main_page_content_list_view(
        slug: str = Path(..., description="slug на главной странице"),
):
    """
    Контент блоков на главной странице
    """
    resources: dict[str, Any] = dict(
        main_page_offer_repo=main_page_repos.MainPageOfferRepo,
        main_page_partner_logo_repo=main_page_repos.MainPagePartnerLogoRepo,
        main_page_sell_online_repo=main_page_repos.MainPageSellOnlineRepo,
    )
    main_page_contents: use_cases.MainPageContentListCase = use_cases.MainPageContentListCase(
        **resources
    )

    return await main_page_contents(slug=slug)
