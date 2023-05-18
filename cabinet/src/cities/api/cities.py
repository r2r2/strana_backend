from typing import Any

from fastapi import APIRouter, status, Depends

from src.cities import repos as cities_repo
from src.cities import use_cases
from src.cities import models
from common import dependencies


router = APIRouter(prefix="/cities", tags=["Cities"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[models.CityModel],
    dependencies=[
        Depends(dependencies.DeletedUserCheck()),
        Depends(dependencies.CurrentAnyTypeUserId())
    ],
)
async def cities_list_view():
    """
    Список городов
    """
    resources: dict[str, Any] = dict(city_repo=cities_repo.CityRepo)
    cities_list: use_cases.CitiesListCase = use_cases.CitiesListCase(**resources)
    return await cities_list()
