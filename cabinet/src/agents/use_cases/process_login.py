from typing import Type

from src.users.use_cases import ProcessLoginCase as BaseProcessLoginCase
from ..exceptions import AgentNotFoundError, AgentNotApprovedError, AgentWrongPasswordError,\
    AgentWasDeletedError


class ProcessLoginCase(BaseProcessLoginCase):
    """
    Процессинг входа для агента
    """
    _NotFoundError: Type[Exception] = AgentNotFoundError
    _WrongPasswordError: Type[Exception] = AgentWrongPasswordError
    _NotApprovedError: Type[Exception] = AgentNotApprovedError
    _WasDeletedError: Type[Exception] = AgentWasDeletedError
