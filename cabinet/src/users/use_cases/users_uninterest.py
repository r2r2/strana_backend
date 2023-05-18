from typing import Type, Any

from ..constants import UserType
from ..mixins import CurrentUserDataMixin
from ..repos import UserRepo, User
from ..entities import BaseUserCase
from ..exceptions import UserNotFoundError
from ..types import UserProperty, UserPropertyRepo
from ..models import RequestUsersUninterestModel


class UsersUninterestCase(BaseUserCase, CurrentUserDataMixin):
    """
    Удаление интересующих объектов пользователю представителем агенства
    """

    def __init__(self, user_repo: Type[UserRepo], property_repo: Type[UserPropertyRepo]) -> None:
        self.user_repo: UserRepo = user_repo()
        self.property_repo: UserPropertyRepo = property_repo()

    async def __call__(
            self,
            user_id: int,
            payload: RequestUsersUninterestModel,
            agency_id: int = None,
            agent_id: int = None,
    ) -> User:
        self.init_user_data(agent_id=agent_id, agency_id=agency_id)
        data: dict[str, Any] = payload.dict()
        uninterested: list[int] = data["uninterested"]
        filters: dict[str, Any] = self.get_user_filters(user_id=user_id)
        user: User = await self.user_repo.retrieve(filters=filters, prefetch_fields=["interested"])
        if not user:
            raise UserNotFoundError
        filters: dict[str, Any] = dict(id__in=uninterested)
        uninterested: list[UserProperty] = await self.property_repo.list(filters=filters)
        interested_ids: list[int] = list(map(lambda x: x.id, list(user.interested)))
        instances: list[UserProperty] = list()
        for uninterest in uninterested:
            if uninterest.id in interested_ids:
                instances.append(uninterest)
        await self.user_repo.rm_m2m(user, relation="interested", instances=instances)
        return user

    def get_user_filters(self, user_id: int) -> dict:
        """Get user filters for agents or represes"""

        current_user_data = self.current_user_data.dict(exclude_none=True)
        return dict(id=user_id, type=UserType.CLIENT, **current_user_data)


class UsersUninterestGlobalIdCase(UsersUninterestCase):
    """
    Удаление интересующих объектов пользователю по global_id
    """

    def __init__(self, user_repo: Type[UserRepo], property_repo: Type[UserPropertyRepo]) -> None:
        self.user_repo: UserRepo = user_repo()
        self.property_repo: UserPropertyRepo = property_repo()

    async def __call__(
            self,
            user_id: int,
            uninterested_global_ids: list[str],
            agency_id: int = None,
            agent_id: int = None,
    ) -> User:
        self.init_user_data(agent_id=agent_id, agency_id=agency_id)
        filters: dict[str, Any] = self.get_user_filters(user_id=user_id)
        user: User = await self.user_repo.retrieve(filters=filters, prefetch_fields=["interested"])
        if not user:
            raise UserNotFoundError
        filters: dict[str, Any] = dict(global_id__in=uninterested_global_ids)
        uninterested: list[UserProperty] = await self.property_repo.list(filters=filters)
        interested_ids: list[int] = list(map(lambda x: x.id, list(user.interested)))
        instances: list[UserProperty] = list()
        for uninterest in uninterested:
            if uninterest.id in interested_ids:
                instances.append(uninterest)
        await self.user_repo.rm_m2m(user, relation="interested", instances=instances)
        return user
