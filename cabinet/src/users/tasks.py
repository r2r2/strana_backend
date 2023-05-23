from asyncio import get_event_loop
from typing import Any

from common import amocrm, requests, utils, email, security
from common.amocrm import repos as amocrm_repos
from common.backend import repos as backend_repos
from config import amocrm_config, backend_config, celery, tortoise_config, logs_config
from src.agents import repos as agents_repos
from src.booking import constants as booking_constants
from src.booking import repos as booking_repos
from src.booking import services as booking_services
from src.booking import tasks as bookings_tasks
from src.buildings import repos as buildings_repos
from src.floors import repos as floors_repos
from src.projects import repos as projects_repos
from src.properties import repos as properties_repos
from src.properties import services as property_services
from src.users import constants as users_constants
from src.users import loggers
from src.users import repos as users_repos
from src.agencies import repos as agencies_repos
from src.users import services
from tortoise import Tortoise


@celery.app.task
def create_amocrm_contact_task(user_id: int, phone: str) -> None:
    """
    Создание контакта в AmoCRM
    """
    import_property_service: property_services.ImportPropertyService = property_services.ImportPropertyService(
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
        create_booking_log_task=bookings_tasks.create_booking_log_task,
        import_property_service=import_property_service,
        statuses_repo=amocrm_repos.AmoStatusesRepo,
        amocrm_config=amocrm_config,
    )
    import_bookings_service: booking_services.ImportBookingsService = booking_services.ImportBookingsService(
        **resources,
    )
    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        import_bookings_service=import_bookings_service,
        amocrm_config=amocrm_config,
    )
    create_contact: services.CreateContactService = services.CreateContactService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(create_contact))(user_id=user_id, phone=phone)
    )


@celery.app.task
def check_client_unique_task(user_id: int, agent_id: int, check_id: int, phone: str) -> bool:
    """
    Проверка клиента на уникальность
    """
    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        agent_repo=agents_repos.AgentRepo,
        amocrm_config=amocrm_config,
    )
    check_unique: services.CheckUniqueService = services.CheckUniqueService(**resources)
    loop: Any = get_event_loop()
    result = loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(check_unique))(
            user_id=user_id, agent_id=agent_id, check_id=check_id, phone=phone
        )
    )
    return result


@celery.app.task
def change_client_agent_task(user_id: int, agent_id: int) -> None:
    """
    Смена агента клиента
    """
    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_config=amocrm_config,
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        agent_repo=agents_repos.AgentRepo,
        booking_substages=booking_constants.BookingSubstages,
    )
    change_agent: services.ChangeAgentService = services.ChangeAgentService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(
        celery.sentry_catch(celery.init_orm(change_agent))(user_id=user_id, agent_id=agent_id)
    )


@celery.app.task
def check_client_task_periodic() -> None:
    """
    Периодическая проверка клиента
    """
    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        agent_repo=agents_repos.AgentRepo,
        booking_substages=booking_constants.BookingSubstages,
        amocrm_config=amocrm_config,
    )
    check_client: services.CheckClientService = services.CheckClientService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(check_client))())


async def update_user_data_task(user_id: int) -> None:
    """
    Импорт данных пользователя из амо
    """

    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        amocrm_config=amocrm_config,
    )
    update_user: services.UpdateUsersService = services.UpdateUsersService(**resources)
    await update_user(user_id=user_id)


@celery.app.task
async def create_user_log_task(log_data: dict[str, Any]) -> None:
    """
    Создание лога пользователя
    """
    resources: dict[str, Any] = dict(
        orm_class=Tortoise, orm_config=tortoise_config, user_log_repo=users_repos.UserLogRepo
    )
    create_log: loggers.CreateUserLogger = loggers.CreateUserLogger(**resources)

    await create_log(log_data=log_data)


@celery.app.task
def check_user_interests() -> None:
    """
    Периодическая проверка избранного для уведомления клиента по почте при наличии изменений
    в объектах недвижимости (цена, статус, акции)
    """
    import_property_service: property_services.ImportPropertyService = property_services.ImportPropertyService(
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
        backend_special_offers_repo=backend_repos.BackendSpecialOfferRepo,
    )
    resources: dict[str, Any] = dict(
        email_class=email.EmailService,
        user_repo=users_repos.UserRepo,
        interests_repo=users_repos.InterestsRepo,
        orm_class=Tortoise,
        orm_config=tortoise_config,
        import_property_service=import_property_service,
        property_repo=properties_repos.PropertyRepo,
        token_creator=security.create_access_token,
    )
    check_client_interests: services.CheckClientInterestService = services.CheckClientInterestService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(check_client_interests))())


@celery.app.task
def periodic_users_clean() -> None:
    """
    Чистка пользователей
    """
    resources: dict[str, Any] = dict(
        user_repo=users_repos.UserRepo,
        orm_class=Tortoise,
        orm_config=tortoise_config,
    )

    clean_users: services.CleanUsersService = services.CleanUsersService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(clean_users))())


@celery.app.task
def periodic_logs_clean() -> None:
    """
    Чистка логов пользователей старше 3 дней
    """
    days: int = logs_config.get("logs_lifetime")
    resources: dict[str, Any] = dict(
        user_log_repo=users_repos.UserLogRepo,
        booking_log_repo=booking_repos.BookingLogRepo,
        agency_log_repo=agencies_repos.AgencyLogRepo,
        orm_class=Tortoise,
        orm_config=tortoise_config,
    )

    clean_logs: services.CleanLogsService = services.CleanLogsService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(clean_logs))(days))


@celery.app.task
def export_user_in_amo(user_id: int) -> None:
    """
    Экспорт пользователя в амо.
    """
    resources: dict[str, Any] = dict(
        orm_class=Tortoise,
        orm_config=tortoise_config,
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
    )
    export_user_in_amo: services.UpdateContactService = services.UpdateContactService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(export_user_in_amo))(user_id=user_id))
