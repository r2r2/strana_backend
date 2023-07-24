from fastapi import APIRouter, Depends, Query

from common.requests import GraphQLRequest
from config import backend_config
from common import dependencies
from src.booking import repos as booking_repos
from src.cities import repos as city_repos
from src.notifications import repos as notifications_repos
from src.users import repos as users_repos
from src.users.models.users_dashboard_specs import ResponseDashboardSpec
from src.users.use_cases.get_users_spec import GetUsersSpecs
from src.users import constants as users_constants

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/specs", response_model=ResponseDashboardSpec)
async def get_specs(
        user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
        city_slug: str = Query(..., description="Город"),
):
    resource = dict(
        users_interested_repos=users_repos.InterestsRepo,
        booking_repos=booking_repos.BookingRepo,
        users_repo=users_repos.UserRepo,
        city_repos=city_repos.CityRepo,
        notifications_model=notifications_repos.ClientNotification,
        request_class=GraphQLRequest,
        backend_config=backend_config
    )
    specs = GetUsersSpecs(**resource)
    return await specs(user_id=user_id, city_slug=city_slug)
