from typing import Type, Callable, Any

from src.users.constants import UserType

from ..entities import BaseAdminCase
from ..exceptions import AdminDataTakenError
from ..models import RequestProcessRegisterModel
from ..repos import AdminRepo, User
from ..types import AdminHasher, AdminSms


class ProcessRegisterCase(BaseAdminCase):
    """
    Процессинг регистрации
    """

    message_template: str = (
        "Вы были зарегистрированы как администратор. Email: {email} Пароль: {password} "
    )

    def __init__(
        self,
        user_type: str,
        sms_class: Type[AdminSms],
        admin_repo: Type[AdminRepo],
        hasher: Callable[..., AdminHasher],
        password_generator: Callable[..., str],
    ) -> None:
        self.admin_repo: AdminRepo = admin_repo()

        self.user_type: str = user_type
        self.hasher: AdminHasher = hasher()
        self.sms_class: Type[AdminSms] = sms_class
        self.password_generator: Callable[..., str] = password_generator

    async def __call__(self, payload: RequestProcessRegisterModel) -> User:
        data: dict[str, Any] = payload.dict()
        phone: str = data["phone"]
        email: str = data["email"]
        filters: dict[str, Any] = dict(type=UserType.ADMIN)
        q_filters = [
            self.admin_repo.q_builder(or_filters=[dict(phone=phone), dict(email__iexact=email)]),
        ]
        admin: User = await self.admin_repo.retrieve(filters=filters, q_filters=q_filters)
        if admin:
            raise AdminDataTakenError
        one_time_password: str = self.password_generator()
        extra_data: dict[str, Any] = dict(
            type=self.user_type, one_time_password=self.hasher.hash(one_time_password),
            is_approved=True, is_active=True,
        )
        data.update(extra_data)
        admin: User = await self.admin_repo.create(data=data)
        sms_options: dict[str, Any] = dict(
            phone=phone,
            message=self.message_template.format(email=email, password=one_time_password),
        )
        self.sms_class(**sms_options).as_task()
        return admin
