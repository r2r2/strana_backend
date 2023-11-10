from datetime import datetime
from typing import Any, Type
from uuid import uuid4

from pytz import UTC

from ..constants import UserType
from ..repos import User, FakeUserPhoneRepo, UserRoleRepo


class FakeSendCodeService:
    """
    Сервис для аутентификации без запроса в СМС центр (для тестовых пользователей)
    """
    def __init__(
        self,
        fake_user_phone_repo: Type[FakeUserPhoneRepo],
        user_role_repo: Type[UserRoleRepo],
    ) -> None:
        self.fake_user_phone_repo = fake_user_phone_repo()
        self.user_role_repo: UserRoleRepo = user_role_repo()
        self.user_type = UserType.CLIENT

    def __call__(self, method):
        async def wrapper(init, payload, real_ip) -> User:
            filters: dict[str, Any] = dict(phone=payload.phone)
            if test_user_phone := await self.fake_user_phone_repo.retrieve(filters=filters):
                data: dict[str, Any] = dict(
                    token=uuid4(),
                    code=test_user_phone.code,
                    code_time=datetime.now(tz=UTC),
                    password=init.hasher.hash(init.password_generator()),
                )
                filters.update(dict(role=await self.user_role_repo.retrieve(filters=dict(slug=self.user_type))))
                user = await init.user_repo.update_or_create(filters=filters, data=data)
                return user
            return await method(init, payload.phone, real_ip)
        return wrapper
