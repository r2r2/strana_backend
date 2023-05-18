from http import HTTPStatus

from src.task_management.entities import BaseTaskException


class TaskChainNotFoundError(BaseTaskException):
    """
    Цепочка заданий не найдена
    """
    status: int = HTTPStatus.NOT_FOUND
    message: str = 'Цепочка заданий не найдена'
    reason: str = 'task_chain_not_found'


class TaskStatusNotFoundError(BaseTaskException):
    """
    Статус задания не найден
    """
    status: int = HTTPStatus.NOT_FOUND
    message: str = 'Статус задания не найден'
    reason: str = 'task_status_not_found'


class TaskInstanceNotFoundError(BaseTaskException):
    """
    Экземпляр задания не найден
    """
    status: int = HTTPStatus.NOT_FOUND
    message: str = 'Экземпляр задания не найден'
    reason: str = 'task_instance_not_found'
