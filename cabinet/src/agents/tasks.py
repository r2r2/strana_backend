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


@celery.app.task
def import_clients_task(agent_id: int) -> None:
    """
    Импорт клиентов агента
    """
    resources: dict[str, Any] = dict(
        user_statuses=users_constants.UserStatus,
        import_bookings_task=booking_tasks.import_bookings_task,
        agent_repo=agents_repos.AgentRepo,
        booking_repo=BookingRepo,
        amocrm_class=amocrm.AmoCRM,
        user_repo=users_repos.UserRepo,
        check_repo=users_repos.CheckRepo,
        orm_class=Tortoise,
        orm_config=tortoise_config,
        booking_substages=booking_constants.BookingSubstages,
        email_class=AgentEmail,
        amocrm_config=amocrm_config,
        statuses_repo=amocrm_repos.AmoStatusesRepo,
    )
    import_clients: services.ImportClientsService = services.ImportClientsService(**resources)
    loop: Any = get_event_loop()
    loop.run_until_complete(celery.sentry_catch(celery.init_orm(import_clients))(agent_id=agent_id))
