from tortoise import Tortoise

from common.settings.repos import BookingSettingsRepo
from config import tortoise_config
from src.booking import repos as booking_repos
from src.task_management import repos as task_management_repos
from src.task_management.services import CreateTaskInstanceService, UpdateTaskInstanceStatusService


class CreateTaskInstanceServiceFactory:
    @staticmethod
    def create() -> CreateTaskInstanceService:
        """
        Создание инстанса сервиса создания задачи для цепочки заданий
        """
        from src.task_management.tasks import update_task_instance_status_task

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


class UpdateTaskInstanceStatusServiceFactory:
    @staticmethod
    def create() -> UpdateTaskInstanceStatusService:
        """
        Создание инстанса сервиса обновления статуса задачи
        """
        from src.task_management.tasks import update_task_instance_status_task
        from src.notifications.tasks import booking_fixation_notification_email_task

        return UpdateTaskInstanceStatusService(
            task_instance_repo=task_management_repos.TaskInstanceRepo,
            task_status_repo=task_management_repos.TaskStatusRepo,
            booking_repo=booking_repos.BookingRepo,
            booking_settings_repo=BookingSettingsRepo,
            update_task_instance_status_task=update_task_instance_status_task,
            booking_fixation_notification_email_task=booking_fixation_notification_email_task,
            orm_class=Tortoise,
            orm_config=tortoise_config,
        )
