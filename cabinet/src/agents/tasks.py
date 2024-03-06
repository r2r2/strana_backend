from asyncio import get_event_loop
from typing import Any

from common import amocrm
from common.amocrm import repos as amocrm_repos
from config import amocrm_config, celery, tortoise_config
from src.agents import repos as agents_repos
from src.agents import services
from src.agents.types import AgentEmail
from src.booking import constants as booking_constants
from src.booking import tasks as booking_tasks
from src.booking.repos import BookingRepo
from src.users import constants as users_constants
from src.users import repos as users_repos
from tortoise import Tortoise
from src.notifications import services as notification_services
from src.notifications import repos as notification_repos


@celery.app.task
def import_clients_task(agent_id: int) -> None:
    """
    Импорт клиентов агента

    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        user_statuses=users_constants.UserStatus,
        import_bookings_task=booking_tasks.import_bookings_task,
        agent_repo=agents_repos.AgentRepo,
        booking_repo=BookingRepo,
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        user_role_repo=users_repos.UserRoleRepo,
        check_repo=users_repos.CheckRepo,
        orm_class=Tortoise,
        orm_config=tortoise_config,
        booking_substages=booking_constants.BookingSubstages,
        email_class=AgentEmail,
        amocrm_config=amocrm_config,
        statuses_repo=amocrm_repos.AmoStatusesRepo,
        get_email_template_service=get_email_template_service,
    )

    import_clients: services.ImportClientsService = services.ImportClientsService(**resources)

    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(import_clients))(agent_id=agent_id))


@celery.app.task
def import_clients_with_all_booking_task(agent_id: int) -> None:
    """
    Импорт клиентов агента и всех их сделок, в том числе закрытых и реализованных

    """
    get_email_template_service: notification_services.GetEmailTemplateService = \
        notification_services.GetEmailTemplateService(
            email_template_repo=notification_repos.EmailTemplateRepo,
        )
    resources: dict[str, Any] = dict(
        user_statuses=users_constants.UserStatus,
        import_bookings_task=booking_tasks.import_bookings_task,
        import_bookings_service=None,
        agent_repo=agents_repos.AgentRepo,
        booking_repo=BookingRepo,
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        user_role_repo=users_repos.UserRoleRepo,
        check_repo=users_repos.CheckRepo,
        orm_class=Tortoise,
        orm_config=tortoise_config,
        booking_substages=booking_constants.BookingSubstages,
        email_class=AgentEmail,
        amocrm_config=amocrm_config,
        statuses_repo=amocrm_repos.AmoStatusesRepo,
        get_email_template_service=get_email_template_service,
    )

    import_clients: services.ImportClientsAllBookingService = services.ImportClientsAllBookingService(**resources)

    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(import_clients))(agent_id=agent_id))
