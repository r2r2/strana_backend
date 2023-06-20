from abc import abstractmethod
from asyncio import Task
from typing import Type, Any

from ..types import RepresSms, RepresEmail
from ..repos import User
from ..entities import BaseRepresCase
# todo: reduce copy-paste from agent code..


class BaseProceedEmailChanges(BaseRepresCase):
    """
    Базовый класс обновления почты
    """
    mail_event_slug: Type[object] = lambda **kwargs: exec("raise NotImplementedError")
    email_link: str = "https://{}/change/repres/change_email?q={}&p={}"
    email_class: Type[object] = lambda **kwargs: exec("raise NotImplementedError")
    site_host: str = None
    get_email_template_service: Type[object] = lambda **kwargs: exec("raise NotImplementedError")

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """Должны быть переопределены email_class и site_host"""
        raise NotImplementedError

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    async def _send_email(self, repres: User, token: str) -> Task:
        update_link: str = self.email_link.format(self.site_host, token, repres.change_email_token)
        email_notification_template = await self.get_email_template_service(
            email_event_slug=self.mail_event_slug,
            context=dict(update_link=update_link, old_email=repres.email, new_email=repres.change_email),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[repres.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: RepresEmail = self.email_class(**email_options)
            return email_service.as_task()


class BaseProceedPhoneChanges(BaseRepresCase):
    """
    Базовый класс обновления телефона
    """
    phone_link: str = "https://{}/change/repres/change_phone?q={}&p={}"
    sms_event_slug: Type[object] = lambda **kwargs: exec("raise NotImplementedError")
    sms_class: Type[object] = lambda **kwargs: exec("raise NotImplementedError")
    site_host: str = None
    get_sms_template_service: Type[object] = lambda **kwargs: exec("raise NotImplementedError")

    async def _send_sms(self, repres: User, token: str) -> Task:
        sms_notification_template = await self.get_sms_template_service(
            sms_event_slug=self.sms_event_slug,
        )

        if sms_notification_template and sms_notification_template.is_active:
            update_link: str = self.phone_link.format(self.site_host, token, repres.change_phone_token)
            message: str = sms_notification_template.template_text.format(
                new_phone=repres.change_phone, old_phone=repres.phone, update_link=update_link
            )
            sms_options: dict[str, Any] = dict(
                phone=repres.phone,
                message=message,
                k_type=sms_notification_template.lk_type.value,
                sms_event_slug=sms_notification_template.sms_event_slug,
            )
            sms_service: RepresSms = self.sms_class(**sms_options)
            return sms_service.as_task()

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """Должны быть переопределены sms_class и site_host"""
        raise NotImplementedError

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError


