from typing import Any

from fastapi import APIRouter, status, Depends, Query, Body, Response, Request

from common.amocrm.components import AmoCRMAvailableMeetingSlots
from src.meetings import repos as meeting_repos
from src.meetings import models, use_cases
from src.users import repos as user_repo
from src.users import constants as user_constants
from src.booking import repos as booking_repos
from src.amocrm import repos as amocrm_repos
from common import dependencies, paginations, amocrm


router = APIRouter(prefix="/meetings", tags=["Meeting"])


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=models.ResponseMeetingsListModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def meeting_list_view(
    statuses: list[str] = Query([], description="Фильтр по статусам", alias='status'),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination()),
):
    """
    Список встреч
    """
    resources: dict[str, Any] = dict(meeting_repo=meeting_repos.MeetingRepo)
    meetings_list: use_cases.MeetingsListCase = use_cases.MeetingsListCase(**resources)
    return await meetings_list(statuses=statuses, pagination=pagination)


@router.get(
    "/slots",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def available_meeting_slots(
    city: str = Query(..., description="Город"),
    obj: str = Query(..., description="Название проекта слитно"),
    meet: list[str] = Query([], description="???"),
):
    """
    Список доступных слотов для записи на встречу
    """
    get_slots: AmoCRMAvailableMeetingSlots = AmoCRMAvailableMeetingSlots()
    payload: dict[str: Any] = dict(city=city, obj=obj, meet=meet)
    return await get_slots(payload=payload)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=models.ResponseCreatedMeetingModel,
)
async def meeting_create_view(
    user_id=Depends(dependencies.CurrentUserId(user_type=user_constants.UserType.CLIENT)),
    payload: models.RequestCreateMeetingModel = Body(...),
):
    """
    Запись на встречу
    """
    resources: dict[str, Any] = dict(
        meeting_repo=meeting_repos.MeetingRepo,
        booking_repo=booking_repos.BookingRepo,
        user_repo=user_repo.UserRepo,
        amocrm_status_repo=amocrm_repos.AmocrmStatusRepo,
        amocrm_class=amocrm.AmoCRM,
    )
    create_meeting: use_cases.CreateMeetingCase = use_cases.CreateMeetingCase(**resources)
    return await create_meeting(user_id=user_id, payload=payload)


@router.patch(
    "{meeting_id}",
    status_code=status.HTTP_200_OK,
    response_model=models.ResponseUpdateMeetingModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def meeting_update_view(
    meeting_id: int,
    payload: models.RequestUpdateMeetingModel = Body(...),
):
    """
    Изменение встречи
    """
    resources: dict[str, Any] = dict(meeting_repo=meeting_repos.MeetingRepo)
    update_meeting: use_cases.UpdateMeetingCase = use_cases.UpdateMeetingCase(**resources)
    return await update_meeting(meeting_id=meeting_id, payload=payload)


@router.delete(
    "{meeting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def meeting_delete_view(meeting_id: int):
    """
    Удаление встречи
    """
    resources: dict[str, Any] = dict(meeting_repo=meeting_repos.MeetingRepo)
    delete_meeting: use_cases.DeleteMeetingCase = use_cases.DeleteMeetingCase(**resources)
    await delete_meeting(meeting_id=meeting_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/confirm", status_code=status.HTTP_201_CREATED)
async def meeting_confirm_webhook(payload: models.RequestConfirmMeetingModel = Body(...)):
    """
    Вебхук подтверждения встречи для AMOCRM
    """
    resources: dict[str, Any] = dict(meeting_repo=meeting_repos.MeetingRepo)
    confirm_meeting: use_cases.ConfirmMeetingCase = use_cases.ConfirmMeetingCase(**resources)
    await confirm_meeting(date=payload.date, meeting_id=payload.amocrm_id)
    return Response(status_code=status.HTTP_201_CREATED)

