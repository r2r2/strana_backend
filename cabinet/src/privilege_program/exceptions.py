from fastapi import status

from .entities import BasePrivilegeException


class PrivilegeProgramNotFoundError(BasePrivilegeException):
    message: str = "Программа привилегий не найдена."
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "privilege_program_not_found"


class PrivilegeCategoryNotFoundError(BasePrivilegeException):
    message: str = "Категория программ привилегий не найдена."
    status: int = status.HTTP_404_NOT_FOUND
    reason: str = "privilege_category_not_found"
