from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Body, Depends, Request, Query, Path

from src.main_page import repos as main_page_repos
from src.main_page import use_cases as main_page_use_cases
from src.main_page import models as main_page_models
from src.users import repos as users_repos
from src.users import use_cases, models

from src.users import filters


router = APIRouter(prefix="/managers", tags=["Managers"])


@router.get(
    "/head_of_partners_department",
    status_code=HTTPStatus.OK,
    response_model=main_page_models.ResponseMainPageManagerRetrieveModel,
)
async def manager_retrieve_view():
    """
    Менеджер на главной странице
    """
    resources: dict[str, Any] = dict(main_page_manager_repo=main_page_repos.MainPageManagerRepo)
    main_page_manager_retrieve: main_page_use_cases.MainPageManagerRetrieveCase =\
        main_page_use_cases.MainPageManagerRetrieveCase(**resources)
    return await main_page_manager_retrieve()


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
