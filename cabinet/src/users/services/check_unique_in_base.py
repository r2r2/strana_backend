from typing import Type, Optional, Any

from src.users.constants import UserType

from ..repos import UserRepo, User
from ..exceptions import NotUniquePhoneUser, NotUniqueEmailUser, NotUniqueEmaiAndPhoneUser
from ..entities import BaseUserService
from ..models import RequestUserCheckUnique


class UserCheckUniqueService(BaseUserService):
    """
    Сервис проверки уникальности пользователя в базе по телефону и почте.
    """

    def __init__(
        self,
        user_repo: Type[UserRepo]
    ) -> None:
        self.user_repo: UserRepo = user_repo()

    async def __call__(
        self,
        payload: RequestUserCheckUnique,
    ) -> None:
        """
        Возвращает ошибку, если пользователь с указанным телефоном или почтой уже есть в базе.
        """

        filters = [
            {"phone": payload.phone},
            {"email": payload.email},
        ]
        exceptions = (
            NotUniquePhoneUser,
            NotUniqueEmailUser,
        )

        raised_exeptions = []
        for filters, exception in zip(filters, exceptions):
            user: Optional[User] = await self.user_repo.retrieve(filters=filters)
            if user:
                exception_data = (exception, user.type)
                raised_exeptions.append(exception_data)
        if len(raised_exeptions) > 1:
            user_type = raised_exeptions[0][1]
            raise self._format_exception(NotUniqueEmaiAndPhoneUser, user_type)
        elif len(raised_exeptions) == 1:
            exeption_data = raised_exeptions.pop()
            raise self._format_exception(exception=exeption_data[0], user_type=exeption_data[1])

    @staticmethod
    def _format_exception(exception: Any, user_type: str):
        """
        Добавляет необходимый тип пользователя в сообщение ошибки.
        """

        if user_type == UserType.AGENT:
            exception.message = exception.message.format("агентом")
        elif user_type == UserType.CLIENT:
            exception.message = exception.message.format("клиентом")
        elif user_type == UserType.REPRES:
            exception.message = exception.message.format("агентством")
        elif user_type == UserType.ADMIN:
            exception.message = exception.message.format("администратором")
        elif user_type == UserType.MANAGER:
            exception.message = exception.message.format("менеджером")
        return exception
