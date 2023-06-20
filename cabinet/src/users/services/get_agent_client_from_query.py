import asyncio
from base64 import b64decode
from typing import Optional, Any, Callable

import structlog
import ujson
from pydantic import BaseModel

from common.handlers.exceptions import get_exc_info
from src.agents.exceptions import AgentNotFoundError
from src.users.constants import UserType
from src.users.entities import BaseUserService
from src.users.exceptions import UserMissMatchError, UserNotFoundError, UserAgentMismatchError
from src.users.repos import UserRepo, User
from src.users.types import UserHasher


class RequestDataDto(BaseModel):
    """
    Модель данных запроса.
    """
    agent_id: int
    client_id: int


class GetAgentClientFromQueryService(BaseUserService):
    """
    Сервис получения агента и клиента из запроса.
    """
    def __init__(
        self,
        user_repo: type[UserRepo],
        hasher: Callable[..., UserHasher],
        logger: Optional[Any] = structlog.getLogger(__name__),
    ):
        self.user_repo: UserRepo = user_repo()
        self.hasher: UserHasher = hasher()
        self.logger = logger

    async def __call__(self, token: str, data: str) -> tuple[User, User]:
        self._verify_data(token=token, data=data)
        user_data: RequestDataDto = self._decode_request_data(data)
        agent, client = await asyncio.gather(
            self.get_agent(user_data=user_data),
            self.get_client_and_validate(user_data=user_data),
        )
        return agent, client

    def _verify_data(self, data: str, token: str):
        """
        Проверяем валидность токена пользователя.
        @param data: str
        @param token: str
        @return: None
        """
        if not self.hasher.verify(data, token):
            raise UserMissMatchError

    def _decode_request_data(self, data: str) -> RequestDataDto:
        """
        Декодирование данных пользователя.
        @param data: str (Закодированный в base64 json)
        @return: RequestDataDto
        """
        try:
            json_data = ujson.loads(b64decode(data))
            return RequestDataDto(**json_data)
        except (ValueError, UnicodeDecodeError, TypeError) as ex:
            self.logger.error('Ошибка во время декодирования данных.', exc_info=get_exc_info(ex))
            raise UserMissMatchError

    async def get_client_and_validate(self, user_data: RequestDataDto) -> User:
        """
        Находим клиента и проверяем его агента
        @param user_data: RequestDataDto
        @return: User
        """
        filters: dict[str, Any] = dict(id=user_data.client_id, type=UserType.CLIENT)
        client: User = await self.user_repo.retrieve(
            filters=filters,
            prefetch_fields=['interested_project', 'interested_project__city'],
        )
        if not client:
            raise UserNotFoundError

        if client.agent_id != user_data.agent_id:
            raise UserAgentMismatchError
        return client

    async def get_agent(self, user_data: RequestDataDto) -> User:
        """
        Находим агента по id
        @param user_data:
        @return:
        """
        filters = dict(id=user_data.agent_id, type=UserType.AGENT)
        agent: User = await self.user_repo.retrieve(
            filters=filters,
            related_fields=['agency'],
        )
        if not agent:
            raise AgentNotFoundError
        return agent
