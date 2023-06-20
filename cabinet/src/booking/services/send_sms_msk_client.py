import asyncio
import json
from base64 import b64encode
from copy import copy
from typing import Optional, Any, Callable, Awaitable

from common.messages import SmsService
from src.booking.repos import BookingRepo, Booking
from src.booking.types import BookingORM
from src.cities.repos import City
from src.notifications.exceptions import SMSTemplateNotFoundError
from src.notifications.repos import AssignClientTemplateRepo, AssignClientTemplate
from src.users.entities import BaseUserService
from src.users.exceptions import UserNotFoundError
from src.users.repos import UserRepo
from src.users.types import UserHasher


class SendSmsToMskClientService(BaseUserService):
    """
    Сервис отправки смс клиенту из Москвы
    """

    def __init__(
        self,
        user_repo: type[UserRepo],
        template_repo: type[AssignClientTemplateRepo],
        sms_class: type[SmsService],
        booking_repo: type[BookingRepo],
        hasher: Callable[..., UserHasher],
        site_config: dict[str, Any],
        orm_class: Optional[BookingORM] = None,
        orm_config: Optional[dict[str, Any]] = None,
    ):
        self.user_repo: UserRepo = user_repo()
        self.template_repo: AssignClientTemplateRepo = template_repo()
        self.booking_repo: BookingRepo = booking_repo()
        self.sms_class: type[SmsService] = sms_class
        self.hasher: UserHasher = hasher()
        self.main_site_host = site_config['main_site_host']

        self.orm_class: Optional[type[BookingORM]] = orm_class
        self.orm_config: Optional[dict[str, Any]] = copy(orm_config)
        if self.orm_config:
            self.orm_config.pop("generate_schemas", None)

    async def __call__(self, booking_id: int, sms_slug: str) -> bool:
        booking: Booking = await self.booking_repo.retrieve(
            filters=dict(id=booking_id),
            prefetch_fields=["user", "agent"],
        )

        user_retrieve_tasks = [
            self.user_repo.retrieve(
                filters=dict(id=booking.user.id, sms_send=False),
                related_fields=[
                    "interested_project",
                    "interested_project__city",
                ],
            ),
            self.user_repo.retrieve(
                filters=dict(id=booking.agent.id),
            ),
        ]
        client, agent = await asyncio.gather(*user_retrieve_tasks)
        if (not client or not client.interested_project) or not agent:
            raise UserNotFoundError

        city: City = client.interested_project.city
        if city.slug != "moskva":
            #  Отправляем смс только клиентам из Москвы
            return False

        template: AssignClientTemplate = await self.template_repo.retrieve(
            filters=dict(city=city, sms__sms_event_slug=sms_slug, sms__is_active=True),
            related_fields=["sms"],
        )
        if not template:
            template: AssignClientTemplate = await self.template_repo.retrieve(
                filters=dict(default=True, sms__is_active=True),
                related_fields=["sms"],
            )
        if not template:
            # Если нет активного шаблона, то не отправляем смс
            return False

        un_assignation_link = self.generate_unassign_link(agent_id=agent.id, client_id=client.id)

        asyncio_tasks: list[Awaitable] = [
            self._send_sms(
                phone=client.phone,
                unassign_link=un_assignation_link,
                agent_name=agent.name,
                sms_template=template.sms.template_text,
            ),
            self.user_repo.update(model=client, data=dict(sms_send=True)),
        ]
        await asyncio.gather(*asyncio_tasks)
        return True

    async def _send_sms(self, phone: str, unassign_link: str, agent_name: str, sms_template: str):
        """
        Отправляем смс клиенту.
        @param phone: str
        @param unassign_link: str
        @param agent_name: str
        """
        sms_options: dict[str, Any] = dict(
            phone=phone,
            message=sms_template.format(unassign_link=unassign_link, agent_name=agent_name),
            tiny_url=True,
        )
        return self.sms_class(**sms_options).as_task()

    def generate_tokens(self, agent_id: int, client_id: int) -> tuple[str, str]:
        """generate_tokens"""
        data = json.dumps(dict(agent_id=agent_id, client_id=client_id))
        b64_data = b64encode(data.encode()).decode()
        b64_data = b64_data.replace("&", "%26")
        token = self.hasher.hash(b64_data)
        return b64_data, token

    def generate_unassign_link(self, agent_id: int, client_id: int) -> str:
        """
        Генерация ссылки для страницы открепления клиента от юзера
        @param agent_id: int
        @param client_id: int
        @return: str
        """
        b64_data, token = self.generate_tokens(agent_id=agent_id, client_id=client_id)
        return f"https://{self.main_site_host}/unassign?t={token}%26d={b64_data}"

