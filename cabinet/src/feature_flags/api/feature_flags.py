from fastapi import APIRouter, status, Request, Query, Depends
from common import dependencies

from ..use_cases.get_feature_flags import GetFeatureFlagsCase

router = APIRouter(prefix="/feature-flags", tags=["feature-flags"])


@router.get("/", status_code=status.HTTP_200_OK)
async def get_feature_flags(
    request: Request,
    user_id: int | None = Depends(dependencies.CurrentOptionalUserIdWithoutRole()),
    feature_flags: list[str] = Query([], description="Список feature flags", alias="feature_flag"),
):
    get_feature_flags_case = GetFeatureFlagsCase(unleash=request.app.unleash)
    return await get_feature_flags_case(feature_flags=feature_flags, user_id=user_id)
