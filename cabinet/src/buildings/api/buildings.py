from typing import Any

from fastapi import APIRouter, status, Query

from src.projects.repos import ProjectRepo
from src.floors.repos import FloorRepo
from ..constants import BuildingTypeRequest
from ..repos import BuildingRepo, BuildingSectionRepo
from ..use_cases import BuildingsListCase, BuildingDetailCase
from ..models.buildings import BuildingDetailResponse

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get("", status_code=status.HTTP_200_OK, response_model=list[BuildingDetailResponse])
async def buildings_list_view(
        project_slug: str = Query(..., alias="project"),
        kind: BuildingTypeRequest = Query(..., alias="kind"),
):
    """
    Список корпусов
    """
    resources: dict[str, Any] = dict(
        building_repo=BuildingRepo,
        project_repo=ProjectRepo,
        building_section_repo=BuildingSectionRepo,
        floor_repo=FloorRepo,
    )
    buildings_list: BuildingsListCase = BuildingsListCase(**resources)
    return await buildings_list(project_slug=project_slug, kind=kind)


@router.get("/{building_id}", status_code=status.HTTP_200_OK, response_model=BuildingDetailResponse)
async def building_detail_view(building_id: int):
    """
    Получение корпуса
    """
    resources: dict[str, Any] = dict(building_repo=BuildingRepo)
    get_building: BuildingDetailCase = BuildingDetailCase(**resources)
    return await get_building(building_id=building_id)
