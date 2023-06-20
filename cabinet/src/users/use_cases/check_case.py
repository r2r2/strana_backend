from datetime import datetime
from typing import Any, Awaitable, Callable, Optional, Type

from pytz import UTC

from src.users.constants import UserType, UserStatus
from ..entities import BaseUserCase
from ..exceptions import UserMissMatchError
from ..models import RequestUsersCheckModel
from ..repos import Check, CheckHistoryRepo, CheckRepo, User, UserRepo


class UsersCheckCase(BaseUserCase):
    """
    Проверка клиента на уникальность
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        check_repo: Type[CheckRepo],
        history_check_repo: Type[CheckHistoryRepo],
        check_unique_service: Callable[..., Awaitable],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.check_repo: CheckRepo = check_repo()

        self.history_check_repo: CheckHistoryRepo = history_check_repo()
        self.check_unique_service: Callable[..., Awaitable] = check_unique_service

        self.agent_pinned: bool = False
        self.repres_pinned: bool = False

    async def __call__(
        self,
        payload: RequestUsersCheckModel,
        agent_id: Optional[int] = None,
        agency_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Check:
        data: dict[str, Any] = payload.dict(exclude_unset=True)
        phone: str = data["phone"]
        filters: dict[str, Any] = dict(phone=phone, type=UserType.CLIENT)
        user: Optional[User] = await self.user_repo.retrieve(filters=filters)

        if payload.email and not user:
            email: str = data["email"]
            filters: dict[str, Any] = dict(email__iexact=email, type=UserType.CLIENT)
            user: User = await self.user_repo.retrieve(filters=filters)
            if user:
                raise UserMissMatchError
        if user:
            user_id = user.id
            self.agent_pinned = True if agent_id and user.agent_id == int(agent_id) else False
            self.repres_pinned = True if agency_id and user.agency_id == agency_id else False

            check: Check = await self._exist_user_check(user=user, phone=phone, agent_id=agent_id)

        else:
            check: Check = await self._not_exist_user_check(phone=phone)
        await check.refresh_from_db(fields=['status'])

        if not agency_id:
            agent_filters: dict = dict(id=agent_id)
            agent: dict = await self.user_repo.retrieve(filters=agent_filters).values("agency_id")
            agency_id: int = agent.get("agency_id")

        history_check_data: dict = dict(
            status=check.status.value,
            client_id=user_id,
            agent_id=agent_id,
            agency_id=agency_id,
            client_phone=phone,
        )
        await self.history_check_repo.create(data=history_check_data)
        return check

    async def _exist_user_check(self, user: User, phone: str, agent_id: int) -> Check:
        """
        Проверяем уникальность в случае, когда пользователь есть в бд.
        Если не нашли привязанную к пользователю проверку - создаём новую.
        """
        filters: dict[str, Any] = dict(user_id=user.id)
        check: Optional[Check] = await self.check_repo.retrieve(filters=filters, ordering='-id')
        if not check:
            data: dict[str, Any] = dict(user_id=user.id, requested=datetime.now(tz=UTC))
            check: Check = await self.check_repo.create(data=data)
        if not check.status_fixed:
            await self.__update_check_status(phone=phone, check=check, user=user, agent_id=agent_id)
        return check

    async def _not_exist_user_check(self, phone: str) -> Check:
        """
        Проверка уникальности в случае, если юзера нет в бд.
        Мы не создаём пользователей в бд и амо до закрепления.
        Для корректного ответа создаём пустую проверку, без привязки к пользователю.
        """
        data: dict[str, Any] = dict(
            requested=datetime.now(tz=UTC),
        )
        check: Check = await self.check_repo.create(data)
        await self.__update_check_status(phone=phone, check=check)
        return check

    async def __update_check_status(
        self,
        phone: str,
        check: Check,
        user: Optional[User] = None,
        agent_id: Optional[int] = None,
    ) -> None:
        """
        Обновляем статус для проверки (Check) в амо.
        Сервис check_unique_service обновляет check.status внутри вызова.
        """
        if self.agent_pinned:
            await self.check_repo.update(check, data={"status": UserStatus.AGENT_PINNED})

        elif self.repres_pinned:
            await self.check_repo.update(check, data={"status": UserStatus.REPRES_PINNED})

        else:
            await self.check_unique_service(phone=phone, check=check, user=user, agent_id=agent_id)
