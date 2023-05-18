from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Type

from ..exceptions import UserAgentHasNoAgency
from ..repos import User


class AbstractHandler(ABC):
    """
    Интерфейс Обработчика объявляет метод построения цепочки обработчиков.
    
    Онтакже объявляет метод для выполнения запроса.
    """
    _NoAgencyError: Type[BaseException] = UserAgentHasNoAgency
    _next_handler: AbstractHandler = None

    def set_next(self, handler:  AbstractHandler) ->  AbstractHandler:
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, user: User) -> Optional[AbstractHandler]:
        if self._next_handler:
            return self._next_handler.handle(user)

        return None


class UserAgencyHandler(AbstractHandler):
    """ 
    Оброботчик проверяет наличие агенства у агента.

    Если агенства нет, авторизация не проходит.
    """
    def handle(self, user: User) -> None:
        if not user.agency:
            raise self._NoAgencyError
        else:
            return super().handle(user)
