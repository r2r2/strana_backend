from abc import abstractmethod
from asyncio import Task
from typing import Type, Any

from ..types import AgentSms, AgentEmail
from ..repos import User
from ..entities import BaseAgentCase


class BaseProceedEmailChanges(BaseAgentCase):
    """
    Базовый класс обновления почты
    """

    mail_event_slug: Type[object] = lambda **kwargs: exec("raise NotImplementedError")
    email_link: str = "https://{}/change/agents/change_email?q={}&p={}"
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
        update_link: str = self.email_link.format(self.site_host, token, agent.change_email_token)
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
    phone_link: str = "https://{}/change/agents/change_phone?q={}&p={}"
    sms_event_slug: Type[object] = lambda **kwargs: exec("raise NotImplementedError")
    sms_class: Type[object] = lambda **kwargs: exec("raise NotImplementedError")
    site_host: str = None
    get_sms_template_service: Type[object] = lambda **kwargs: exec("raise NotImplementedError")

    async def _send_sms(self, agent: User, token: str) -> Task:
        sms_notification_template = await self.get_sms_template_service(
            sms_event_slug=self.sms_event_slug,
        )

        if sms_notification_template and sms_notification_template.is_active:
            update_link: str = self.phone_link.format(self.site_host, token, agent.change_phone_token)
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


