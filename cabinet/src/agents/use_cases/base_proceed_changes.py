from abc import abstractmethod
from asyncio import Task
from typing import Type, Any

from ..types import AgentSms, AgentEmail
from ..repos import User
from ..entities import BaseAgentCase
from common.schemas import UrlEncodeDTO
from common.utils import generate_notify_url


class BaseProceedEmailChanges(BaseAgentCase):
    """
    Базовый класс обновления почты
    """

    mail_event_slug: Type[object] = lambda **kwargs: exec("raise NotImplementedError")
    email_link_route_template: str = "/change/agents/change_email"
    email_class: Type[object] = lambda **kwargs: exec("raise NotImplementedError")
    get_email_template_service: Type[object] = lambda **kwargs: exec("raise NotImplementedError")
    site_host: str = None

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """Должны быть переопределены email_class и site_host"""
        raise NotImplementedError

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    async def _send_email(self, agent: User, token: str) -> Task:
        url_data: dict[str, Any] = dict(
            host=self.site_host,
            route_template = self.email_link_route_template,
            query_params = dict(
                q = token,
                p = agent.change_email_token,
            )
        )
        url_dto: UrlEncodeDTO = UrlEncodeDTO(**url_data)
        update_link: str = generate_notify_url(url_dto=url_dto)
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=dict(
                update_link=update_link, old_email=agent.email, new_email=agent.change_email
            ),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[agent.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: AgentEmail = self.email_class(**email_options)
            return email_service.as_task()


class BaseProceedPhoneChanges(BaseAgentCase):
    """
    Базовый класс обновления телефона
    """
    phone_link_route_template: str = "/change/agents/change_phone"
    sms_event_slug: Type[object] = lambda **kwargs: exec("raise NotImplementedError")
    sms_class: Type[object] = lambda **kwargs: exec("raise NotImplementedError")
    site_host: str = None
    get_sms_template_service: Type[object] = lambda **kwargs: exec("raise NotImplementedError")

    async def _send_sms(self, agent: User, token: str) -> Task:
        sms_notification_template = await self.get_sms_template_service(
            sms_event_slug=self.sms_event_slug,
        )

        if sms_notification_template and sms_notification_template.is_active:
            url_data: dict[str, Any] = dict(
                host=self.site_host,
                route_template=self.phone_link_route_template,
                query_params=dict(
                    q=token,
                    p=agent.change_phone_token,
                ),
                use_ampersand_ascii=True,
            )
            url_dto: UrlEncodeDTO = UrlEncodeDTO(**url_data)
            update_link: str = generate_notify_url(url_dto=url_dto)
            sms_options: dict[str, Any] = dict(
                phone=agent.phone,
                message=sms_notification_template.template_text.format(
                    new_phone=agent.change_phone, old_phone=agent.phone, update_link=update_link
                ),
                lk_type=sms_notification_template.lk_type.value,
                sms_event_slug=sms_notification_template.sms_event_slug,
            )
            sms_service: AgentSms = self.sms_class(**sms_options)
            return sms_service.as_task()

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """Должны быть переопределены sms_class и site_host"""
        raise NotImplementedError

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError


