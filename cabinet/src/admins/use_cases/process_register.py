from typing import Type, Callable, Any

from src.users.constants import UserType

from ..entities import BaseAdminCase
from ..exceptions import AdminDataTakenError
from ..models import RequestProcessAdminRegisterModel
from ..repos import AdminRepo, User
from ..types import AdminHasher, AdminSms


class ProcessRegisterCase(BaseAdminCase):
    """
    Процессинг регистрации
    """
    sms_event_slug = "register_admin"

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

    async def __call__(self, payload: RequestProcessAdminRegisterModel) -> User:
        data: dict[str, Any] = payload.dict()
        phone: str = data.get("phone")
        email: str = data.get("email")
        password: str = data.pop("password")
        filters: dict[str, Any] = dict(type=UserType.ADMIN)
        q_filters = [
            self.admin_repo.q_builder(or_filters=[dict(phone=phone), dict(email__iexact=email)]),
        ]
        admin: User = await self.admin_repo.retrieve(filters=filters, q_filters=q_filters)
        if admin:
            raise AdminDataTakenError
        extra_data: dict[str, Any] = dict(
            type=self.user_type,
            is_approved=False,
            is_active=False,
            password=self.hasher.hash(password),
        )
        data.update(extra_data)
        admin: User = await self.admin_repo.create(data=data)
        return admin
