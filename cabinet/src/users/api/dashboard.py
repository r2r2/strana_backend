from fastapi import APIRouter, Query, Depends

from common import dependencies
from common.calculator.calculator import CalculatorAPI
from common.requests import CommonRequest
from common.backend import repos as backend_repos
from config import mc_backend_config
from src.booking import repos as booking_repos
from src.cities import repos as city_repos
from src.notifications import repos as notifications_repos
from src.users import constants as users_constants
from src.users import repos as users_repos
from src.users.models.users_dashboard_specs import ResponseDashboardSpec
from src.users.use_cases.get_users_spec import GetUsersSpecs

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/specs", response_model=ResponseDashboardSpec)
async def get_specs(
        user_id: int = Depends(dependencies.CurrentUserId(user_type=users_constants.UserType.CLIENT)),
        city: str = Query(..., description="Город"),
):
    calc_resource = dict(
        request_class=CommonRequest,
        calculator_config=mc_backend_config,
    )
    calculator_class = CalculatorAPI(**calc_resource)
    resource = dict(
        users_interested_repos=users_repos.InterestsRepo,
        booking_repos=booking_repos.BookingRepo,
        city_repos=city_repos.CityRepo,
        notifications_model=notifications_repos.ClientNotification,
        calculator_class=calculator_class,
        backend_properties_repo=backend_repos.BackendPropertiesRepo,
    )
    specs = GetUsersSpecs(**resource)
    return await specs(user_id=user_id, city_slug=city)
