from http import HTTPStatus

from src.projects.entities import BaseProjectException


class ProjectNotFoundError(BaseProjectException):
    message: str = "Проект не найден."
    status: int = HTTPStatus.NOT_FOUND
    reason: str = "project_not_found"
