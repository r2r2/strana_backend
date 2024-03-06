from typing import Any
from http import HTTPStatus
from fastapi import APIRouter, Request, Query
import random

from src.tips import models, use_cases
from src.tips import repos as tips_repos


router = APIRouter(prefix="/tips", tags=["Tips"])


@router.get("", status_code=HTTPStatus.OK, response_model=models.ResponseTipListModel)
async def tip_list_view(request: Request):
    """
    Список подсказок
    """
    context = dict(userId=random.randint(1000, 9999))
    enabled: bool = request.app.unleash.is_enabled(request.app.feature_flags.strana_lk_1230, context=context)

    if enabled:
        return dict(
            count=999,
            result=[],
        )

    resources: dict[str, Any] = dict(tip_repo=tips_repos.TipRepo)
    tip_list: use_cases.TipListCase = use_cases.TipListCase(**resources)
    return await tip_list()
