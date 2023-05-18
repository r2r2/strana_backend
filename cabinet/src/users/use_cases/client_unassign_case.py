import datetime
import json
from asyncio import Task
from typing import Type, Callable, Any, Optional, Tuple
from base64 import b64decode, b64encode
from urllib import parse

import structlog
from pydantic import BaseModel

from common.amocrm import AmoCRM
from common.amocrm.constants import AmoElementTypes, AmoTaskTypes
from common.email import EmailService
from common.handlers.exceptions import get_exc_info
from config import site_config
from src.agents.exceptions import AgentNotFoundError
from src.agents.types import AgentEmail, AgentSms
from src.booking.repos import BookingRepo
from src.users.constants import UserType
from src.users.entities import BaseUserCase
from src.users.exceptions import UserMissMatchError, UserAgentMismatchError, UserNotFoundError
from src.users.models import ResponseUnAssigned, ResponseUnassignClient
from src.users.repos import UserRepo, User
from src.users.types import UserHasher
from src.admins.repos import AdminRepo


class RequestDataDto(BaseModel):
    agent_id: int
    client_id: int


class UnAssignationCase(BaseUserCase):
    """Кейс для формирования и отправки ссылки открепления клиента от агента"""
    def __init__(
            self,
            user_repo: Type[UserRepo],
            hasher: Callable[..., UserHasher],
            logger: Optional[Any] = structlog.getLogger(__name__),
    ):
        self.user_repo: UserRepo = user_repo()
        self.hasher: UserHasher = hasher()
        self.lk_site_host = site_config['site_host']
        self.logger = logger

    async def __call__(self, token: str, data: str) -> ResponseUnAssigned:
        self._verify_data(token=token, data=data)
        user_data: RequestDataDto = self._decode_request_data(data)
        client: User = await self.get_client_and_validate(user_data=user_data)
        agent: User = await self.get_agent(user_data=user_data)

        un_assign_link = self.generate_unassign_link(agent_id=user_data.agent_id, client_id=user_data.client_id)

        return ResponseUnAssigned(
            agent_name=agent.full_name, client_name=client.full_name, unassign_link=un_assign_link
        )

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
            json_data = json.loads(b64decode(data))
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
        client: User = await self.user_repo.retrieve(filters=filters)
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
        agent: User = await self.user_repo.retrieve(filters=filters)
        if not agent:
            raise AgentNotFoundError
        return await self.user_repo.retrieve(filters=filters)

    def generate_tokens(self, agent_id: int, client_id: int) -> Tuple[bytes, str]:
        data = json.dumps(dict(client_id=client_id, agent_id=agent_id))
        b64_data = b64encode(data.encode())
        token = self.hasher.hash(b64_data)
        return b64_data, token

    def generate_unassign_link(self, agent_id: int, client_id: int) -> str:
        """
        Генерация ссылки для открепления клиента от юзера
        @param agent_id: int
        @param client_id: int
        @return: str
        """

        b64_data, token = self.generate_tokens(agent_id=agent_id, client_id=client_id)
        params = dict(t=token, d=b64_data)
        return f"https://{self.lk_site_host}/api/users/client/unassign?{parse.urlencode(params)}"


class UnassignCase(BaseUserCase):
    manager_email_template = 'src/users/templates/manager_unassign_client.html'
    agent_email_template = 'src/users/templates/agent_unassign_client.html'
    task_message = 'Связаться: Позвонить клиенту, он нажал кнопку "Открепиться", проверь на случайность и ' \
                   'обязательно заполни резервный комментарий к задаче.'

    def __init__(
            self,
            user_repo: Type[UserRepo],
            admin_repo: Type[AdminRepo],
            booking_repo: Type[BookingRepo],
            email_class: Type[AgentEmail],
            amocrm_class: Type[AmoCRM],
            sms_class: Type[AgentSms],
            hasher: Callable[..., UserHasher],
            email_recipients: dict,
            logger: Optional[Any] = structlog.getLogger(__name__),
    ):
        self.user_repo: UserRepo = user_repo()
        self.admin_repo = admin_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.email_class: Type[AgentEmail] = email_class
        self.amocrm_class: Type[AmoCRM] = amocrm_class
        self.sms_class: Type[AgentSms] = sms_class
        self.hasher: UserHasher = hasher()
        self.logger = logger
        self.strana_manager = email_recipients['strana_manager']

        # note: временный ответственный, пока не известна логика получения
        self.responsible_manager_amocrm_id = 6541746

    async def __call__(self, token: str, data: str) -> ResponseUnassignClient:
        self._verify_data(token=token, data=data)
        user_data: RequestDataDto = self._decode_request_data(data)
        client: User = await self.get_client_and_validate(user_data=user_data)
        await self._create_task_for_manager(client_amocrm_id=client.amocrm_id)
        agent: User = await self.get_agent(user_data=user_data)

        filters = dict(type=UserType.ADMIN, receive_admin_emails=True)
        admins = await self.admin_repo.list(filters=filters)

        await self._send_manager_email(
                recipients=[admin.email for admin in admins],
                client_name=client.full_name,
                agent_name=agent.full_name
        )

        return ResponseUnassignClient.from_orm(client)

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
            json_data = json.loads(b64decode(data))
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
        client: User = await self.user_repo.retrieve(filters=filters)
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
        agent: User = await self.user_repo.retrieve(filters=filters)
        if not agent:
            raise AgentNotFoundError
        return await self.user_repo.retrieve(filters=filters)

    async def _send_manager_email(self, recipients: list[str], **context) -> Task:
        """
        Уведомляем менеджера страны о закреплении клиента.
        @param recipients: list[str]
        @param context: Any (Контекст, который будет использоваться в шаблоне письма)
        @return: Task
        """
        email_options: dict[str, Any] = dict(
            topic="Отказ от закрепления клиента",
            template=self.manager_email_template,
            recipients=recipients,
            context=context
        )
        email_service: EmailService = self.email_class(**email_options)
        return email_service.as_task()

    async def _create_task_for_manager(self, client_amocrm_id: int):
        complete_till_datetime = datetime.datetime.now() + datetime.timedelta(days=2)

        async with await self.amocrm_class() as amocrm:
            await amocrm.create_task(
                element_id=client_amocrm_id,
                element_type=AmoElementTypes.CONTACT,
                task_type=AmoTaskTypes.CALL,
                text=self.task_message,
                complete_till=int(complete_till_datetime.timestamp()),
                responsible_user_id=self.responsible_manager_amocrm_id
            )
