from asyncio import Task
from secrets import token_urlsafe
from typing import Any, Callable, Type

from ..entities import BaseUserCase
from ..exceptions import UserEmailTakenError, UserNotFoundError
from ..models import RequestUpdatePersonalModel
from ..repos import User, UserRepo
from ..types import UserAmoCRM, UserEmail
from ..loggers.wrappers import user_changes_logger
from src.notifications.services import GetEmailTemplateService


class UpdatePersonalCase(BaseUserCase):
    """
    Обновление персональных данных
    """

    mail_event_slug = "user_partial_update"
    link: str = "https://{}/confirm/users/confirm_email?q={}&p={}"

    def __init__(
        self,
        user_repo: Type[UserRepo],
        site_config: dict[str, Any],
        email_class: Type[UserEmail],
        amocrm_class: Type[UserAmoCRM],
        token_creator: Callable[[int], str],
        get_email_template_service: GetEmailTemplateService,
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.user_update = user_changes_logger(
            self.user_repo.update, self, content="Обновление данных пользователя без смены email"
        )
        self.email_changed_update = user_changes_logger(
            self.user_repo.update, self, content="Обновление токена для смены почты"
        )
        self.email_class: Type[UserEmail] = email_class
        self.amocrm_class: Type[UserAmoCRM] = amocrm_class
        self.token_creator: Callable[[int], str] = token_creator
        self.get_email_template_service = get_email_template_service

        self.site_host: str = site_config["site_host"]

    async def __call__(self, payload: RequestUpdatePersonalModel, user_id: int) -> User:
        data: dict[str, Any] = payload.dict()
        email: str = data["email"]
        filters: dict[str, Any] = dict(id=user_id)
        user: User = await self.user_repo.retrieve(filters=filters)
        if not user:
            raise UserNotFoundError
        email_changed: bool = email != user.email
        user: User = await self.user_update(user=user, data=data)
        if not user:
            raise UserEmailTakenError
        await self._amocrm_update(user=user)
        if email_changed:
            data: dict[str, Any] = dict(is_approved=False, email_token=token_urlsafe(32))
            await self.email_changed_update(user=user, data=data)
            token: str = self.token_creator(user.id)
            await self._send_email(user=user, token=token)
        return user

    async def _amocrm_update(self, user: User):
        """
        Обновление контакта в амо
        """
        async with await self.amocrm_class() as amocrm:
            contact_options: dict[str, Any] = dict(
                user_phone=user.phone,
                user_email=user.email,
                user_id=user.amocrm_id,
                user_birth_date=user.birth_date,
                user_name=f"{user.surname} {user.name} {user.patronymic}",
                user_passport=f"{user.passport_series} {user.passport_number}",
            )
            await amocrm.update_contact(**contact_options)

    async def _send_email(self, user: User, token: str) -> Task:
        """
        Отправка письма
        """
        confirm_link: str = self.link.format(self.site_host, token, user.email_token)
        email_notification_template = await self.get_email_template_service(
            mail_event_slug=self.mail_event_slug,
            context=dict(confirm_link=confirm_link),
        )

        if email_notification_template and email_notification_template.is_active:
            email_options: dict[str, Any] = dict(
                topic=email_notification_template.template_topic,
                content=email_notification_template.content,
                recipients=[user.email],
                lk_type=email_notification_template.lk_type.value,
                mail_event_slug=email_notification_template.mail_event_slug,
            )
            email_service: UserEmail = self.email_class(**email_options)
            return email_service.as_task()
