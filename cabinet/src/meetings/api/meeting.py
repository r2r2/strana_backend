from typing import Any

from fastapi import APIRouter, Body, Depends, Path, Query, status

from common import amocrm, dependencies, paginations, email
from common.amocrm.components import AmoCRMAvailableMeetingSlots
from common.settings.repos import BookingSettingsRepo
from src.amocrm import repos as amocrm_repos
from src.booking import repos as booking_repos
from src.cities import repos as city_repo
from src.events import repos as event_repo
from src.meetings import models, repos as meeting_repos, use_cases
from src.projects.repos import ProjectRepo
from src.users import repos as user_repo
from src.notifications import repos as notification_repos, services as notification_services
from src.task_management import services as task_management_services, repos as task_management_repos
from src.task_management.tasks import update_task_instance_status_task
from src.notifications.tasks import booking_fixation_notification_email_task
from src.cities.repos import CityRepo
from src.meetings import models
from src.meetings import repos as meeting_repos
from src.meetings import use_cases
from src.projects.repos import ProjectRepo
from src.task_management.factories import UpdateTaskInstanceStatusServiceFactory
from src.users import repos as user_repo
from src.cities import repos as city_repo
from src.events import repos as event_repo
from src.amocrm.repos import AmocrmGroupStatusRepo
from src.notifications import repos as notification_repos
from src.notifications import services as notification_services


router = APIRouter(prefix="/meetings", tags=["Meeting"])


@router.get(
    "/slots",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def available_meeting_slots(
        city: str = Query(..., description="Slug города"),
        project: int | None = Query(None, description="Id проекта"),
        meet: list[str] = Query([], description="???"),
):
    """
    Список доступных слотов для записи на встречу
    """
    resources: dict[str, Any] = dict(
        project_repo=ProjectRepo,
        city_repo=city_repo.CityRepo,
    )
    get_slots: AmoCRMAvailableMeetingSlots = AmoCRMAvailableMeetingSlots(**resources)
    return await get_slots(city_slug=city, meet=meet, project_id=project)


@router.get(
    "/statuses",
    status_code=status.HTTP_200_OK,
    response_model=list[models.ResponseMeetingsStatusListModel],
)
async def meeting_statuses_list_view():
    """
    Список статусов встреч из админки.
    """
    resources: dict[str, Any] = dict(
        status_meeting_repo=meeting_repos.MeetingStatusRepo,
    )
    meetings_list: use_cases.MeetingsStatusListCase = use_cases.MeetingsStatusListCase(**resources)
    return await meetings_list()


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=models.ResponseMeetingsListModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def meeting_list_view(
    statuses: list[str] = Query([], description="Фильтр по статусам", alias='status'),
    client_id: int = Query(default=None, description="Фильтр по клиентам"),
    booking_id: int = Query(default=None, description="Фильтр по бронированию"),
    pagination: paginations.PagePagination = Depends(dependencies.Pagination()),
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
):
    """
    Список встреч.
    """
    resources: dict[str, Any] = dict(
        meeting_repo=meeting_repos.MeetingRepo,
        user_repo=user_repo.UserRepo,
    )
    meetings_list: use_cases.MeetingsListCase = use_cases.MeetingsListCase(**resources)
    return await meetings_list(
        pagination=pagination,
        client_id=client_id,
        booking_id=booking_id,
        statuses=statuses,
        user_id=user_id,
    )


@router.get(
    "/{meeting_id}",
    status_code=status.HTTP_200_OK,
    response_model=models.ResponseDetailMeetingModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def meeting_detail_view(
    meeting_id: int = Path(...),
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
):
    """
    Деталка встречи.
    """
    resources: dict[str, Any] = dict(
        meeting_repo=meeting_repos.MeetingRepo,
        meeting_status_repo=meeting_repos.MeetingStatusRepo,
        booking_settings_repo=BookingSettingsRepo,
        user_repo=user_repo.UserRepo,
        check_repo=user_repo.CheckRepo,
        amocrm_group_status_repo=amocrm_repos.AmocrmGroupStatusRepo,
        user_pinning_repo=user_repo.UserPinningStatusRepo,
    )
    meetings_detail: use_cases.MeetingsDetailCase = use_cases.MeetingsDetailCase(**resources)
    return await meetings_detail(meeting_id=meeting_id, user_id=user_id)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=models.ResponseCreatedMeetingModel,
)
async def meeting_create_view(
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
    payload: models.RequestCreateMeetingModel = Body(...),
):
    """
    Запись на встречу.
    """
    update_task_instance_status_service = UpdateTaskInstanceStatusServiceFactory.create()
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        meeting_repo=meeting_repos.MeetingRepo,
        meeting_status_repo=meeting_repos.MeetingStatusRepo,
        meeting_creation_source_repo=meeting_repos.MeetingCreationSourceRepo,
        calendar_event_repo=event_repo.CalendarEventRepo,
        booking_repo=booking_repos.BookingRepo,
        user_repo=user_repo.UserRepo,
        city_repo=city_repo.CityRepo,
        amocrm_status_repo=amocrm_repos.AmocrmStatusRepo,
        amocrm_pipeline_repo=amocrm_repos.AmocrmPipelineRepo,
        amocrm_group_status_repo=amocrm_repos.AmocrmGroupStatusRepo,
        amocrm_class=amocrm.AmoCRM,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
        update_task_instance_status_service=update_task_instance_status_service,
    )
    create_meeting: use_cases.CreateMeetingCase = use_cases.CreateMeetingCase(**resources)
    return await create_meeting(user_id=user_id, payload=payload)


@router.patch(
    "/{meeting_id}",
    status_code=status.HTTP_200_OK,
    response_model=models.ResponseUpdateMeetingModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def meeting_update_view(
    meeting_id: int,
    payload: models.RequestUpdateMeetingModel = Body(...),
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
):
    """
    Изменение встречи.
    """
    update_task_instance_status_service = UpdateTaskInstanceStatusServiceFactory.create()

    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        meeting_repo=meeting_repos.MeetingRepo,
        meeting_status_repo=meeting_repos.MeetingStatusRepo,
        calendar_event_repo=event_repo.CalendarEventRepo,
        user_repo=user_repo.UserRepo,
        booking_repo=booking_repos.BookingRepo,
        amocrm_status_repo=amocrm_repos.AmocrmStatusRepo,
        amocrm_class=amocrm.AmoCRM,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
        update_task_instance_status_service=update_task_instance_status_service,
    )
    update_meeting: use_cases.UpdateMeetingCase = use_cases.UpdateMeetingCase(**resources)
    return await update_meeting(meeting_id=meeting_id, user_id=user_id, payload=payload)


@router.patch(
    "/{meeting_id}/refuse",
    status_code=status.HTTP_200_OK,
    response_model=models.ResponseUpdateMeetingModel,
    dependencies=[Depends(dependencies.DeletedUserCheck())],
)
async def meeting_refuse_view(
    meeting_id: int,
    user_id: int = Depends(dependencies.CurrentAnyTypeUserId()),
):
    """
    Отмена встречи.
    """
    update_task_instance_status_service = UpdateTaskInstanceStatusServiceFactory.create()
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        meeting_repo=meeting_repos.MeetingRepo,
        meeting_status_repo=meeting_repos.MeetingStatusRepo,
        user_repo=user_repo.UserRepo,
        booking_repo=booking_repos.BookingRepo,
        amocrm_status_repo=amocrm_repos.AmocrmStatusRepo,
        amocrm_class=amocrm.AmoCRM,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
        update_task_instance_status_service=update_task_instance_status_service,
    )
    refuse_meeting: use_cases.RefuseMeetingCase = use_cases.RefuseMeetingCase(**resources)
    return await refuse_meeting(meeting_id=meeting_id, user_id=user_id)
