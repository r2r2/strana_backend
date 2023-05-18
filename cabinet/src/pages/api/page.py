from typing import Any
from http import HTTPStatus
from fastapi import APIRouter

from src.pages import models, use_cases
from src.pages import repos as pages_repos


router = APIRouter(prefix="/pages", tags=["Pages"])


@router.get(
    "/broker_registration",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseBrokerRegistrationModel,
)
async def broker_registration_retrieve_view():
    """
    Страница регистрации брокера
    """
    resources: dict[str, Any] = dict(broker_registration_repo=pages_repos.BrokerRegistrationRepo)
    broker_registration: use_cases.BrokerRegistrationRetrieveCase = use_cases.BrokerRegistrationRetrieveCase(
        **resources
    )
    return await broker_registration()


@router.get(
    "/check_unique", status_code=HTTPStatus.OK, response_model=models.ResponseCheckUniqueModel
)
async def check_unique_retrieve_view():
    """
    Страница проверки на уникальность
    """
    resources: dict[str, Any] = dict(check_unique_repo=pages_repos.CheckUniqueRepo)
    check_unique: use_cases.CheckUniqueRetrieveCase = use_cases.CheckUniqueRetrieveCase(**resources)
    return await check_unique()


@router.get(
    "/showtime_registration",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseShowtimeRegistrationModel,
)
async def showtime_registration_retrieve_view():
    """
    Страница записи на показ
    """
    resources: dict[str, Any] = dict(
        showtime_registration_repo=pages_repos.ShowtimeRegistrationRepo
    )
    showtime_registration: use_cases.ShowtimeRegistrationRetrieveCase = use_cases.ShowtimeRegistrationRetrieveCase(
        **resources
    )
    return await showtime_registration()
