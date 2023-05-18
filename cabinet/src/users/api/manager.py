from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Body, Depends, Request, Query, Path

from src.users import repos as users_repos
from src.users import use_cases, models

from src.users import filters


router = APIRouter(prefix="/managers", tags=["Managers"])


@router.get(
    "/{manager_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseManagerRetrieveModel,
)
async def manager_retrieve_view(
    manager_id: int = Path(...),
):
    """
    Менеджер
    """
    resources: dict[str, Any] = dict(
        manager_repo=users_repos.ManagersRepo,
    )

    manager_retrieve: use_cases.ManagerRetrieveCase = use_cases.ManagerRetrieveCase(**resources)
    return await manager_retrieve(manager_id=manager_id)


@router.get(
    "",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseManagersListModel,
)
async def managers_search(
    init_filters: dict[str, Any] = Depends(filters.ManagerFilter.filterize),
):
    """
    Поиск менеджера
    """
    resources: dict[str, Any] = dict(
        manager_repo=users_repos.ManagersRepo,
    )

    manager_list: use_cases.ManagersListCase = use_cases.ManagersListCase(**resources)
    return await manager_list(init_filters=init_filters)
