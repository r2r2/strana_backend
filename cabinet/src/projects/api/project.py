from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends, Query

from common import paginations, dependencies
from src.projects import models, use_cases
from src.projects import repos as projects_repos
from src.getdoc import repos as getdoc_repos
from ..models import Status


router = APIRouter(prefix="/projects", tags=["Project"])
router_v2 = APIRouter(prefix="/v2/projects", tags=["Project", "v2"])


@router.get("", status_code=HTTPStatus.OK, response_model=models.ResponseProjectsListModel)
async def projects_list_view(
    status: Status = Query(None, alias="status"),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination(page_size=12)),
):
    """
    Список проектов
    """
    resources: dict[str, Any] = dict(project_repo=projects_repos.ProjectRepo)
    projects_list: use_cases.ProjectsListCase = use_cases.ProjectsListCase(**resources)
    return await projects_list(status=status, pagination=pagination)


@router_v2.get("", status_code=HTTPStatus.OK, response_model=list[models.ResponseAdditionalProjectsListModel])
async def projects_list_view_v2(
    status: Status = Query(None, alias="status"),
):
    """
    Список проектов (для api v2)
    """
    resources: dict[str, Any] = dict(
        project_repo=projects_repos.ProjectRepo,
        additional_template_repo=getdoc_repos.AdditionalAgreementTemplateRepo,
    )
    projects_list: use_cases.AdditionalProjectsListCase = use_cases.AdditionalProjectsListCase(**resources)
    return await projects_list(status=status)
