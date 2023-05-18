from typing import Type

from src.users.use_cases import ProcessLoginCase as BaseProcessLoginCase
from ..exceptions import RepresWrongPasswordError, RepresNotFoundError, RepresNotApprovedError,\
    RepresWasDeletedError


class ProcessLoginCase(BaseProcessLoginCase):
    """
    Процессинг входа
    """
    _NotFoundError: Type[Exception] = RepresNotFoundError
    _WrongPasswordError: Type[Exception] = RepresWrongPasswordError
    _NotApprovedError: Type[Exception] = RepresNotApprovedError
    _WasDeletedError: Type[Exception] = RepresWasDeletedError
