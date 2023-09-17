from typing import Any
from http import HTTPStatus
from fastapi import APIRouter

from src.tips import models, use_cases
from src.tips import repos as tips_repos


router = APIRouter(prefix="/tips", tags=["Tips"])


@router.get("", status_code=HTTPStatus.OK, response_model=models.ResponseTipListModel)
async def tip_list_view():
    """
    Список подсказок
    """

    resources: dict[str, Any] = dict(tip_repo=tips_repos.TipRepo)
    tip_list: use_cases.TipListCase = use_cases.TipListCase(**resources)
    return await tip_list()
