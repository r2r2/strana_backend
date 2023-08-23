from http import HTTPStatus
from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.params import Query

from common import dependencies, paginations
from src.menu import use_cases
from src.menu.models import ResponseMenuListModel
from src.menu import repos as menu_repos
from src.users import repos as users_repos

router = APIRouter(prefix="/menu", tags=["menu"])


@router.get("", status_code=HTTPStatus.OK, response_model=ResponseMenuListModel)
async def get_menu(
        city: str = Query(..., description="Город"),
        user_id: Optional[int] = Depends(dependencies.CurrentOptionalUserIdWithoutRole()),
):
    """
    Список пунктов меню
    """

    resources: dict[str, Any] = dict(
        menu_repos=menu_repos.MenuRepo,
        user_repos=users_repos.UserRepo,
        role_repos=users_repos.UserRoleRepo,
    )
    meetings_list: use_cases.GetMenuUseCase = use_cases.GetMenuUseCase(**resources)
    return await meetings_list(city=city, user_id=user_id)
