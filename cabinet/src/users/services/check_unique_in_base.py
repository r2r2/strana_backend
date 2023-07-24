from enum import Enum
from typing import Type, Optional, Any

from src.users.constants import UserType
from ..repos import UserRepo, User
from ..exceptions import NotUniquePhoneUser, NotUniqueEmailUser, NotUniqueEmaiAndPhoneUser
from ..entities import BaseUserService
from ..models import RequestUserCheckUnique


class UserMatchType(str, Enum):
    """
    Тип пользователя со склонением
    """
    ADMIN: str = "админом"
    AGENT: str = "агентом"
    CLIENT: str = "клиентом"
    REPRES: str = "агентством"
    MANAGER: str = "менеджером"


class UserCheckUniqueService(BaseUserService):
    """
    Сервис проверки уникальности пользователя в базе по телефону и почте.
    """

    mail_and_phone_match_message: str = "Простите, данная почта закреплена за другим {mail_match_user_type}, " \
                                        "телефон закреплен за другим {phone_match_user_type}, вы не можете их использовать."
    mail_match_message: str = "Простите, данная почта закреплена за другим {}, вы не можете её использовать."
    phone_match_message: str = "Простите, данный номер телефона закреплен за другим {}, вы не можете его использовать."

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
            {
                "phone": payload.phone,
                "type__not_in": [UserType.CLIENT],
            },
            {
                "email": payload.email,
                "type__not_in": [UserType.CLIENT],
            },
        ]
        exceptions = (
            NotUniquePhoneUser,
            NotUniqueEmailUser,
        )

        raised_exceptions = []
        for filters, exception in zip(filters, exceptions):
            user: Optional[User] = await self.user_repo.retrieve(filters=filters)
            if user:
                if user.type == UserType.AGENT:
                    user_type = UserMatchType.AGENT
                elif user.type == UserType.CLIENT:
                    user_type = UserMatchType.CLIENT
                elif user.type == UserType.REPRES:
                    user_type = UserMatchType.REPRES
                elif user.type == UserType.ADMIN:
                    user_type = UserMatchType.ADMIN
                else:
                    user_type = UserMatchType.MANAGER

                exception_data = (exception, user_type)
                raised_exceptions.append(exception_data)

        if raised_exceptions:
            raise self._format_exceptions(raised_exceptions)

    def _format_exceptions(self, raised_exceptions: list[Any]):
        """
        Добавляет необходимый тип пользователя в сообщение ошибки.
        """

        if len(raised_exceptions) == 2:
            exception = NotUniqueEmaiAndPhoneUser
            phone_match_user_type = raised_exceptions[0][1]
            mail_match_user_type = raised_exceptions[1][1]
            message = self.mail_and_phone_match_message.format(
                mail_match_user_type=mail_match_user_type,
                phone_match_user_type=phone_match_user_type,
            )
            exception.message = message
        else:
            exception = raised_exceptions[0][0]
            user_type = raised_exceptions[0][1]
            if exception == NotUniqueEmailUser:
                message = self.mail_match_message.format(user_type)
            else:
                message = self.phone_match_message.format(user_type)
            exception.message = message

        return exception
