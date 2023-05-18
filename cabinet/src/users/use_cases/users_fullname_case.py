from typing import Type, Union

from src.users.constants import UserType
from src.users.entities import BaseUserCase
from src.users.exceptions import UserNotFoundError, UserNoAgentError
from src.users.models import UserFullnameModel
from src.users.repos import UserRepo, User


class UsersFullnameCase(BaseUserCase):
    """ Кейс получения имени, фамилии и отчества у юзера"""

    def __init__(
            self,
            user_repo: Type[UserRepo],
            user_type: Union[UserType.AGENT, UserType.CLIENT]
    ):
        self.user_repo: UserRepo = user_repo()
        self.user_type = user_type

    async def __call__(self, user_id: int) -> UserFullnameModel:
        filters: dict = dict(type=self.user_type, id=user_id)
        user: User = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserNotFoundError
        return UserFullnameModel.from_orm(user)


class AgentsFullnameByClientCase(UsersFullnameCase):
    """ Кейс для получения имени, фамилии, отчества агента по id клиента"""

    async def __call__(self, user_id) -> UserFullnameModel:
        filters = dict(type=UserType.CLIENT, id=user_id)
        client: User = await self.user_repo.retrieve(filters=filters, prefetch_fields=["agent"])
        if not client:
            raise UserNotFoundError
        if not client.agent:
            raise UserNoAgentError

        return await super().__call__(user_id=client.agent.id)
