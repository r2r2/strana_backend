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

    email_template: str = "src/repres/templates/change_email.html"
    email_link: str = "https://{}/change/repres/change_email?q={}&p={}"
    email_class: Type[object] = lambda **kwargs: exec("raise NotImplementedError")
    email_topic = "Смена почты"
    site_host: str = None

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """Должны быть переопределены email_class и site_host"""
        raise NotImplementedError

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    async def _send_email(self, repres: User, token: str) -> Task:
        update_link: str = self.email_link.format(self.site_host, token, repres.change_email_token)
        email_options: dict[str, Any] = dict(
            topic=self.email_topic,
            recipients=[repres.email],
            template=self.email_template,
            context=dict(
                update_link=update_link, old_email=repres.email, new_email=repres.change_email
            ),
        )
        email_service: RepresEmail = self.email_class(**email_options)
        return email_service.as_task()


class BaseProceedPhoneChanges(BaseRepresCase):
    """
    Базовый класс обновления телефона
    """
    phone_link: str = "https://{}/change/repres/change_phone?q={}&p={}"
    message_template: str = (
        "Для подтверждения смены номера телефона {old_phone} на {new_phone} перейдите по ссылке {update_link} . "
        "После перехода по ссылке Ваш аккаунт будет неактивен до подтверждения номера телефона {new_phone} ."
    )
    sms_class: Type[object] = lambda **kwargs: exec("raise NotImplementedError")
    site_host: str = None

    async def _send_sms(self, repres: User, token: str) -> Task:
        update_link: str = self.phone_link.format(self.site_host, token, repres.change_phone_token)
        message: str = self.message_template.format(
            new_phone=repres.change_phone, old_phone=repres.phone, update_link=update_link
        )
        sms_options: dict[str, Any] = dict(phone=repres.phone, message=message)
        sms_service: RepresSms = self.sms_class(**sms_options)
        return sms_service.as_task()

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """Должны быть переопределены sms_class и site_host"""
        raise NotImplementedError

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError


