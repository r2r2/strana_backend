from asyncio import get_event_loop
from typing import Any, Optional

import structlog

from common import amocrm, email, messages, profitbase, requests, security, utils
from common.amocrm import repos as amo_repos
from common.celery.utils import redis_lock
from config import amocrm_config, backend_config, celery, site_config, tortoise_config
from src.agents import repos as agents_repos
from src.amocrm import repos as src_amocrm_repos
from src.booking import loggers
from src.booking import repos as booking_repos
from src.booking import services
from src.booking.factories import ActivateBookingServiceFactory
from src.buildings import repos as buildings_repos
from src.cities import repos as cities_repos
from src.floors import repos as floors_repos
from src.notifications import repos as notifications_repos
from src.notifications import services as notification_services
from src.notifications import tasks as notification_tasks
from src.projects import repos as projects_repos
from src.properties import repos as properties_repos
from src.properties.services import ImportPropertyServiceFactory
from src.task_management.factories import UpdateTaskInstanceStatusServiceFactory
from src.task_management.tasks import update_task_instance_status_task
from src.users import constants as users_constants
from src.users import repos as users_repos
from tortoise import Tortoise
from src.amocrm.repos import AmocrmStatusRepo


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
def check_booking_task(booking_id: int, status: Optional[str] = '') -> None:
    """
    Отложенная проверка бронирования
    """
    logger = structlog.getLogger("check_booking_task")
    logger.info(f'Starting check_booking_task for booking_id={booking_id}')
    update_task_instance_status_service = UpdateTaskInstanceStatusServiceFactory.create()
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notifications_repos.EmailTemplateRepo,
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
        booking_notification_sms_task=notification_tasks.booking_notification_sms_task,
    )
    check_booking: services.CheckBookingService = services.CheckBookingService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(check_booking))(booking_id=booking_id, status=status)
    )
    logger.info(f'Finished check_booking_task for booking_id={booking_id}')


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
    import_property_service = ImportPropertyServiceFactory.create(orm_class=Tortoise, orm_config=tortoise_config)

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
        amocrm_status_repo=src_amocrm_repos.AmocrmStatusRepo,
        update_task_instance_status_task=update_task_instance_status_task,
        check_booking_task=check_booking_task,
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
    lock_id = "periodic_cache_update_bookings_task"
    can_launch = redis_lock(lock_id)
    if not can_launch:
        return

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
    update_bookings: services.ActivateBookingService = ActivateBookingServiceFactory.create()
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
