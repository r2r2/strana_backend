from tortoise import Tortoise

from common.settings.repos import BookingSettingsRepo
from config import tortoise_config
from src.booking import repos as booking_repos
from src.task_management import repos as task_management_repos
from src.task_management.services import CreateTaskInstanceService
from src.task_management.tasks import update_task_instance_status_task


class CreateTaskInstanceServiceFactory:
    @staticmethod
    def create() -> CreateTaskInstanceService:
        """
        Создание инстанса сервиса создания задачи для цепочки заданий
        """
        return CreateTaskInstanceService(
            booking_repo=booking_repos.BookingRepo,
            task_instance_repo=task_management_repos.TaskInstanceRepo,
            task_chain_repo=task_management_repos.TaskChainRepo,
            task_status_repo=task_management_repos.TaskStatusRepo,
            booking_settings_repo=BookingSettingsRepo,
            update_task_instance_status_task=update_task_instance_status_task,
            orm_class=Tortoise,
            orm_config=tortoise_config,
        )
