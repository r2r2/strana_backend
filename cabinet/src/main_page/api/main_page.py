from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Path
from src.main_page import models
from src.main_page import repos as main_page_repos
from src.main_page import use_cases

router = APIRouter(prefix="/main_page", tags=["MainPage"])


@router.get(
    "/content",
    status_code=HTTPStatus.OK,
    response_model=list[models.MainPageContentDetailResponse],
)
async def main_page_content_list_view():
    """
    Контент и заголовки главной страницы
    """
    resources: dict[str, Any] = dict(main_page_content_repo=main_page_repos.MainPageContentRepo)
    main_page_contents: use_cases.MainPageContentListCase = use_cases.MainPageContentListCase(
        **resources
    )

    return await main_page_contents()


@router.get(
    "/offers",
    status_code=HTTPStatus.OK,
    response_model=list[models.MainPageOfferDetailResponse],
)
async def main_page_offer_list_view():
    """
    Главная страница. Что мы предлагаем
    """
    resources: dict[str, Any] = dict(main_page_offer_repo=main_page_repos.MainPageOfferRepo)
    main_page_offers: use_cases.MainPageOfferListCase = use_cases.MainPageOfferListCase(
        **resources
    )

    return await main_page_offers()


@router.get(
    "/partner_logos",
    status_code=HTTPStatus.OK,
    response_model=list[models.MainPagePartnerLogoDetailResponse],
)
async def main_page_partner_logo_list_view():
    """
    Главная страница. Логотипы партнёров
    """
    resources: dict[str, Any] = dict(main_page_partner_logo_repo=main_page_repos.MainPagePartnerLogoRepo)
    main_page_partner_logo_list: use_cases.MainPagePartnerLogoListCase = use_cases.MainPagePartnerLogoListCase(
        **resources
    )

    return await main_page_partner_logo_list()


@router.get(
    "/sell_online",
    status_code=HTTPStatus.OK,
    response_model=list[models.MainPageSellOnlineDetailResponse],
)
async def main_page_sell_online_list_view():
    """
    Главная страница. Продавайте онлайн
    """
    resources: dict[str, Any] = dict(main_page_sell_online_repo=main_page_repos.MainPageSellOnlineRepo)
    main_page_sell_online_list: use_cases.MainPageSellOnlineListCase = use_cases.MainPageSellOnlineListCase(
        **resources
    )

    return await main_page_sell_online_list()


@router.get(
    "/sell_online",
    status_code=HTTPStatus.OK,
    response_model=list[models.MainPageSellOnlineDetailResponse],
)
async def main_page_manager_view():
    """
    Главная страница. Менеджер
    """
    resources: dict[str, Any] = dict(main_page_sell_online_repo=main_page_repos.MainPageSellOnlineRepo)
    main_page_sell_online_list: use_cases.MainPageSellOnlineListCase = use_cases.MainPageSellOnlineListCase(
        **resources
    )

    return await main_page_sell_online_list()


@router.get(
    "/manager/{manager_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseManagerRetrieveModel,
)
async def manager_retrieve_view(manager_id: int = Path(...)):
    """
    Менеджер
    """
    resources: dict[str, Any] = dict(main_page_manager_repo=main_page_repos.MainPageManagerRepo)
    main_page_manager_retrieve: use_cases.MainPageManagerRetrieveCase = use_cases.MainPageManagerRetrieveCase(
        **resources)
    return await main_page_manager_retrieve(manager_id=manager_id)
