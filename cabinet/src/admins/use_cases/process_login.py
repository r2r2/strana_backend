from typing import Type

from src.users.use_cases import ProcessLoginCase as BaseProcessLoginCase
from ..exceptions import AdminWrongPasswordError, AdminNotFoundError, AdminWasDeletedError


class ProcessLoginCase(BaseProcessLoginCase):
    """
    Процессинг входа
    """
    _WrongPasswordError: Type[Exception] = AdminWrongPasswordError
    _NotFoundError: Type[Exception] = AdminNotFoundError
    _WasDeletedError: Type[Exception] = AdminWasDeletedError
