from http import HTTPStatus

from .entities import BaseManagerException


class ManagerNotFoundError(BaseManagerException):
    message: str = "Менеджер не найден."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "manager_not_found"
