from typing import Any

from fastapi import APIRouter, status, Request

from common.requests import CommonRequest
from src.cities import models
from src.cities import repos as cities_repo
from src.cities import use_cases

router = APIRouter(prefix="/cities", tags=["Cities"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[models.CityModel],
)
async def cities_list_view():
    """
    Список городов
    """
    resources: dict[str, Any] = dict(city_repo=cities_repo.CityRepo)
    cities_list: use_cases.CitiesListCase = use_cases.CitiesListCase(**resources)
    return await cities_list()


@router.get(
    "/current",
    status_code=status.HTTP_200_OK,
    response_model=models.CityModel
)
async def current_city(request: Request):
    """
    Список городов
    """
    resources: dict[str, Any] = dict(
        cities_repo=cities_repo.CityRepo,
        iplocation_repo=cities_repo.IPLocationRepo,
        request_class=CommonRequest,
    )
    cities_list: use_cases.CurrentCity = use_cases.CurrentCity(**resources)
    return await cities_list(request.client.host)
