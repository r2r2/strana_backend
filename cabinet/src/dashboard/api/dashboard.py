from typing import Optional

from fastapi import APIRouter, Query, Depends

from common import dependencies
from common.calculator.calculator import CalculatorAPI
from common.portal.portal import PortalAPI
from common.requests import GraphQLRequest, CommonRequest
from config import mc_backend_config, backend_config
from src.cities import repos as cities_repos
from src.users import repos as users_repos
from src.booking import repos as booking_repos
from src.dashboard import repos as dashboard_repos
from src.dashboard.models.block import BlockListResponse
from src.dashboard.models.slide import ResponseGetSlider
from src.dashboard.use_cases.get_dashboard_list import GetDashboardListCase
from src.dashboard.use_cases.get_slider_list import GetSliderListCase


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=list[BlockListResponse])
async def get_block_list(
        city: str = Query(..., description="Город"),
        user_id: Optional[int] = Depends(dependencies.CurrentOptionalUserIdWithoutRole()),
):
    resources = dict(
        dashboard_block=dashboard_repos.BlockRepo,
        elements_repo=dashboard_repos.ElementRepo,
        city_repo=cities_repos.CityRepo,
        user_repo=users_repos.UserRepo,
        booking_repo=booking_repos.BookingRepo,
        link_repo=dashboard_repos.LinkRepo,
        portal_class=PortalAPI(request_class=GraphQLRequest, portal_config=backend_config),
        calculator_class=CalculatorAPI(request_class=CommonRequest, calculator_config=mc_backend_config),
        mc_config=mc_backend_config,
        portal_config=backend_config
    )
    get_list: GetDashboardListCase = GetDashboardListCase(**resources)
    return await get_list(city_slug=city, user_id=user_id)


@router.get(
    "/slides", 
    response_model=list[ResponseGetSlider]
    )
async def get_slider_list():
    resources = dict(
        slider_repo=dashboard_repos.SliderRepo,
    )
    get_list: GetSliderListCase = GetSliderListCase(**resources)
    return await get_list()
