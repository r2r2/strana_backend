from datetime import datetime
from typing import Any, Callable, Type
from uuid import uuid4

from fastapi import BackgroundTasks
from pytz import UTC

from ..constants import UserType
from ..entities import BaseUserCase
from ..loggers.wrappers import user_changes_logger
from ..repos import NotificationMuteRepo, RealIpUsersRepo, User, UserRepo, FakeUserPhoneRepo, UserRoleRepo, UserRole
from ..services.notification_condition import NotificationConditionService
from ..services.fake_send_code import FakeSendCodeService
from ..types import UserHasher, UserSms
from src.notifications.services import GetSmsTemplateService

notification_condition_service = NotificationConditionService(
        user_repo=UserRepo,
        real_ip_repo=RealIpUsersRepo,
        notification_mute_repo=NotificationMuteRepo,
    )
fake_send_code_service = FakeSendCodeService(
        fake_user_phone_repo=FakeUserPhoneRepo,
    )


class SendCodeCase(BaseUserCase):
    """
    Отправка кода
    """

    sms_event_slug = "user_send_code"
    client_role_slug = "client"

    def __init__(
        self,
        update_user_data: Any,
        sms_class: Type[UserSms],
        user_repo: Type[UserRepo],
        role_repo: Type[UserRoleRepo],
        get_sms_template_service: GetSmsTemplateService,
        hasher: Callable[..., UserHasher],
        background_tasks: BackgroundTasks,
        code_generator: Callable[..., str],
        password_generator: Callable[..., str],
    ) -> None:
        self.hasher: UserHasher = hasher()
        self.user_repo: UserRepo = user_repo()
        self.role_repo: UserRoleRepo = role_repo()
        self.user_update_or_create = user_changes_logger(
            self.user_repo.update_or_create, self, content="Создание или обновление"
        )

        self.sms_class: Type[UserSms] = sms_class
        self.update_client_data = update_user_data
        self.code_generator: Callable[..., str] = code_generator
        self.background_tasks: BackgroundTasks = background_tasks
        self.password_generator: Callable[..., str] = password_generator
        self.get_sms_template_service: GetSmsTemplateService = get_sms_template_service

    @fake_send_code_service
    @notification_condition_service
    async def __call__(self, phone: str) -> User:
        client_role: UserRole = await self.role_repo.retrieve(filters=dict(slug=self.client_role_slug))
        filters: dict[str, Any] = dict(phone=phone, type=UserType.CLIENT)

        data: dict[str, Any] = dict(
            token=uuid4(),
            role=client_role,
            code=self.code_generator(),
            code_time=datetime.now(tz=UTC),
            password=self.hasher.hash(self.password_generator()),
        )
        user = await self.user_update_or_create(filters=filters, data=data)
        if user.amocrm_id:
            self.background_tasks.add_task(self.update_client_data, user.id)

        sms_notification_template = await self.get_sms_template_service(
            sms_event_slug=self.sms_event_slug,
        )

        if sms_notification_template and sms_notification_template.is_active:
            sms_options: dict[str, Any] = dict(
                message=sms_notification_template.template_text.format(
                    code=data['code'],
                ),
                phone=phone,
                lk_type=sms_notification_template.lk_type.value,
                sms_event_slug=sms_notification_template.sms_event_slug,
            )
            self.sms_class(**sms_options).as_task()

        return user
