from asyncio import get_event_loop
from typing import Any, Optional

from tortoise import Tortoise

from common import amocrm, profitbase, requests, utils, email, messages, security
from common.amocrm import repos as amo_repos
from common.backend import repos as backend_repos
from config import amocrm_config, backend_config, celery, tortoise_config, site_config
from src.agents import repos as agents_repos
from src.booking import loggers
from src.booking import repos as booking_repos
from src.booking import services
from src.buildings import repos as buildings_repos
from src.cities import repos as cities_repos
from src.floors import repos as floors_repos
from src.notifications import repos as notifications_repos
from src.projects import repos as projects_repos
from src.properties import repos as properties_repos
from src.properties import services as property_services
from src.task_management import repos as task_management_repos
from src.task_management import services as task_management_services
from src.users import constants as users_constants
from src.users import repos as users_repos
from src.users import services as user_services
from src.amocrm.repos import AmocrmStatusRepo
from src.notifications import services as notification_services
from src.notifications import repos as notification_repos


@celery.app.task
def create_booking_log_task(log_data: dict[str, Any]) -> None:
    """
    Создание лога бронирования
    """
    resources: dict[str, Any] = dict(
        booking_log_repo=booking_repos.BookingLogRepo, orm_class=Tortoise, orm_config=tortoise_config,
    )
    create_log: loggers.CreateBookingLogLogger = loggers.CreateBookingLogLogger(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(create_log))(log_data=log_data))


async def create_booking_log_task_v2(log_data: dict[str, Any]) -> None:
    """
    Создание лога бронирования без celery
    """
    resources: dict[str, Any] = dict(
        orm_class=Tortoise, orm_config=tortoise_config, booking_log_repo=booking_repos.BookingLogRepo
    )
    create_log: loggers.CreateBookingLogLogger = loggers.CreateBookingLogLogger(**resources)
    await create_log(log_data=log_data)


@celery.app.task
def create_amocrm_log_task(note_data: dict[str, Any]) -> None:
    """
    Создание заметки
    """
    resources: dict[str, Any] = dict(amocrm_class=amocrm.AmoCRM)
    create_log: loggers.CreateAmoCRMLogLogger = loggers.CreateAmoCRMLogLogger(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(create_log)(note_data=note_data))


@celery.app.task
def check_booking_task(booking_id: int, status: Optional[str] = None) -> None:
    """
    Отложенная проверка бронирования
    """
    resources: dict[str, Any] = dict(
        task_instance_repo=task_management_repos.TaskInstanceRepo,
        task_status_repo=task_management_repos.TaskStatusRepo,
        booking_repo=booking_repos.BookingRepo,
    )
    update_task_instance_status_service = task_management_services.UpdateTaskInstanceStatusService(
        **resources
    )
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        backend_config=backend_config,
        check_booking_task=check_booking_task,
        request_class=requests.GraphQLRequest,
        profitbase_class=profitbase.ProfitBase,
        booking_repo=booking_repos.BookingRepo,
        amocrm_status_repo=AmocrmStatusRepo,
        property_repo=properties_repos.PropertyRepo,
        create_booking_log_task=create_booking_log_task,
        update_task_instance_status_service=update_task_instance_status_service,
        email_class=email.EmailService,
        get_email_template_service=get_email_template_service,
    )
    check_booking: services.CheckBookingService = services.CheckBookingService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(check_booking))(booking_id=booking_id, status=status)
    )


@celery.app.task
def deactivate_expired_bookings_task_periodic() -> None:
    """
    Деактивация бронирований, которые почему-то не были
    деактивированы по таймеру в check_booking_task.
    """
    deactivate_expired_bookings = services.DeactivateExpiredBookingsService(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        backend_config=backend_config,
        request_class=requests.GraphQLRequest,
        profitbase_class=profitbase.ProfitBase,
        booking_repo=booking_repos.BookingRepo,
        property_repo=properties_repos.PropertyRepo,
        create_booking_log_task=create_booking_log_task,
    )
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(deactivate_expired_bookings))())


@celery.app.task
def import_bookings_task(user_id: int) -> None:
    """
    Импорт бронирований
    """
    import_property_service = property_services.ImportPropertyService(
        floor_repo=floors_repos.FloorRepo,
        global_id_decoder=utils.from_global_id,
        global_id_encoder=utils.to_global_id,
        project_repo=projects_repos.ProjectRepo,
        building_repo=buildings_repos.BuildingRepo,
        property_repo=properties_repos.PropertyRepo,
        building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
        backend_building_booking_type_repo=backend_repos.BackendBuildingBookingTypesRepo,
        backend_properties_repo=backend_repos.BackendPropertiesRepo,
        backend_floors_repo=backend_repos.BackendFloorsRepo,
        backend_sections_repo=backend_repos.BackendSectionsRepo,
    )

    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        backend_config=backend_config,
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
        floor_repo=floors_repos.FloorRepo,
        user_types=users_constants.UserType,
        global_id_encoder=utils.to_global_id,
        request_class=requests.GraphQLRequest,
        booking_repo=booking_repos.BookingRepo,
        project_repo=projects_repos.ProjectRepo,
        building_repo=buildings_repos.BuildingRepo,
        property_repo=properties_repos.PropertyRepo,
        create_booking_log_task=create_booking_log_task,
        import_property_service=import_property_service,
        statuses_repo=amo_repos.AmoStatusesRepo,
        amocrm_config=amocrm_config,
    )
    import_bookings_service = services.ImportBookingsService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(import_bookings_service))(user_id=user_id)
    )


@celery.app.task
def update_bookings_task() -> None:
    """
    Обновление существующих бронирований
    """
    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        backend_config=backend_config,
        amocrm_config=amocrm_config,
        floor_repo=floors_repos.FloorRepo,
        global_id_encoder=utils.to_global_id,
        request_class=requests.GraphQLRequest,
        booking_repo=booking_repos.BookingRepo,
        project_repo=projects_repos.ProjectRepo,
        building_repo=buildings_repos.BuildingRepo,
        property_repo=properties_repos.PropertyRepo,
        statuses_repo=amo_repos.AmoStatusesRepo,
        cities_repo=cities_repos.CityRepo,
    )
    update_bookings: services.UpdateBookingsService = services.UpdateBookingsService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(update_bookings))())


async def deactivate_bookings_task(booking_data: dict) -> None:
    """
    Деактивация бронирования
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        property_repo=properties_repos.PropertyRepo,
        request_class=requests.GraphQLRequest,
        webhook_request_repo=booking_repos.WebhookRequestRepo,
    )
    update_bookings: services.DeactivateBookingsService = services.DeactivateBookingsService(**resources)
    await update_bookings(**booking_data)


async def activate_bookings_task(booking_data: dict) -> None:
    """
    Активация бронирования
    """
    resources: dict[str, Any] = dict(
        booking_repo=booking_repos.BookingRepo,
        property_repo=properties_repos.PropertyRepo,
        request_class=requests.GraphQLRequest,
        webhook_request_repo=booking_repos.WebhookRequestRepo,
    )
    update_bookings: services.ActivateBookingsService = services.ActivateBookingsService(**resources)
    await update_bookings(**booking_data)


async def activate_booking_task(booking_data: dict) -> None:
    """
    Общая активация бронирования
    """
    resources: dict[str, Any] = dict(
        create_amocrm_log_task=create_amocrm_log_task,
        create_booking_log_task=create_booking_log_task,
        booking_repo=booking_repos.BookingRepo,
        amocrm_class=amocrm.AmoCRM,
        profitbase_class=profitbase.ProfitBase,
        global_id_decoder=utils.from_global_id,
        building_booking_type_repo=buildings_repos.BuildingBookingTypeRepo,
        property_repo=properties_repos.PropertyRepo,
        request_class=requests.UpdateSqlRequest,
    )
    update_bookings: services.ActivateBookingService = services.ActivateBookingService(**resources)
    await update_bookings(**booking_data)


@celery.app.task
def change_booking_status_task(booking_id: int, status: str) -> None:
    """
    Изменение статуса бронирования, если не оплачено
    """
    change_booking_status = services.ChangeBookingStatusService(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        booking_repo=booking_repos.BookingRepo,
    )
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(change_booking_status))(booking_id=booking_id, status=status)
    )


@celery.app.task
def send_sms_to_msk_client_task(booking_id: int, sms_slug: str) -> None:
    """
    Отправка смс клиенту, если бронь в МСК
    """
    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        user_repo=users_repos.UserRepo,
        booking_repo=booking_repos.BookingRepo,
        template_repo=notifications_repos.AssignClientTemplateRepo,
        sms_class=messages.SmsService,
        hasher=security.get_hasher,
        site_config=site_config,
    )
    send_sms_to_msk_client: services.SendSmsToMskClientService = services.SendSmsToMskClientService(
        **resources
    )
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(send_sms_to_msk_client))(booking_id=booking_id, sms_slug=sms_slug)
    )


@celery.app.task
def export_booking_in_amo(booking_id: int) -> None:
    """
    Экспорт бронирования в амо.
    """
    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        booking_repo=booking_repos.BookingRepo,
        create_amocrm_log_task=create_amocrm_log_task,
    )
    export_booking_in_amo: services.UpdateAmoBookingService = services.UpdateAmoBookingService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(export_booking_in_amo))(booking_id=booking_id))
