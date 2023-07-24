from http import HTTPStatus
from common.dependencies.users import CurrentAnyTypeUserId
from fastapi import APIRouter, Depends, Query
from src.cautions.repos import CautionRepo, CautionMuteRepo
from src.cautions.services.available_cautions import AvailableCautionsForUserService
from src.cautions import models
from src.users import repos as users_repos
from src.cautions import use_cases

from src.users.repos import UserRepo

router = APIRouter(prefix="/cautions", tags=["Cautions"])


@router.get(
    "",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseCautionListModel,
    summary="Получение предупреждений"
)
async def caution_list(
    user_id: int = Depends(CurrentAnyTypeUserId())
):
    """
    Получение списка всех предупреждений для текущего пользователя
    """
    caution_service: AvailableCautionsForUserService = AvailableCautionsForUserService(
        user_repo=users_repos.UserRepo,
        caution_repo=CautionRepo
    )
    caution_list_case: use_cases.CautionListCase = use_cases.CautionListCase(
        caution_service=caution_service
    )
    return dict(warnings=await caution_list_case(user_id=user_id))


@router.delete(
    "/{caution_id}",
    status_code=HTTPStatus.OK,
    response_model=models.ResponseCautionMuteModel,
    summary="Заглушение предупреждения"
)
async def cautions_mute(
    caution_id: int,
    user_id: int = Depends(CurrentAnyTypeUserId())
):
    resources = dict(
        user_repo=UserRepo,
        caution_repo=CautionRepo,
        caution_mute_repo=CautionMuteRepo
    )
    mute_caution: use_cases.CautionMuteCase = use_cases.CautionMuteCase(**resources)
    await mute_caution(user_id=user_id, caution_id=caution_id)
    return models.ResponseCautionMuteModel()
