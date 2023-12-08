import asyncio
from typing import Any, Optional, Type, Union

from src.agencies.repos import Agency, AgencyRepo
from src.properties.services import ImportPropertyService

from ..constants import UserType, SlugType
from ..entities import BaseUserCase
from ..exceptions import UserNoProjectError, UserNotFoundError
from ..loggers.wrappers import user_changes_logger
from ..mixins import CurrentUserDataMixin
from ..models import RequestUsersInterestModel
from ..repos import User, UserRepo
from ..types import (UserInterestedRepo, UserProject, UserProjectRepo,
                     UserProperty, UserPropertyRepo)


class UsersInterestCase(BaseUserCase, CurrentUserDataMixin):
    """
    Добавления интересующих объектов пользователю
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        agency_repo: Type[AgencyRepo],
        interests_repo: Type[UserInterestedRepo],
        project_repo: Type[UserProjectRepo],
        property_repo: Type[UserPropertyRepo],
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.user_update = user_changes_logger(
            self.user_repo.update, self, content="Обновление интересов пользователей"
        )
        self.agency_repo: AgencyRepo = agency_repo()
        self.project_repo: UserProjectRepo = project_repo()
        self.property_repo: UserPropertyRepo = property_repo()
        self.interests_repo: UserInterestedRepo = interests_repo()

    async def __call__(
            self,
            user_id: int,
            payload: RequestUsersInterestModel,
            agent_id: int = None,
            agency_id: int = None
    ) -> User:
        self.init_user_data(agent_id=agent_id, agency_id=agency_id)
        data: dict[str, Any] = payload.dict()
        project_id: Union[int, None] = data.pop("interested_project", None)
        interested: list[str] = data.pop("interested", list())
        filters: dict[str, Any] = self.get_user_filters(user_id=user_id)
        user: User = await self.user_repo.retrieve(
            filters=filters, prefetch_fields=["interested", "agent"]
        )
        if not user:
            raise UserNotFoundError
        current_user: User = await self.get_current_user()
        filters: dict[str, Any] = dict(id=project_id)
        if project_id:
            projects: list[UserProject] = await self.project_repo.list(filters=filters)
            if not projects:
                raise UserNoProjectError
        data["interested_project_id"]: int = project_id
        filters: dict[str, Any] = dict(id__in=interested)
        interested: list[UserProperty] = await self.property_repo.list(filters=filters)
        interested_ids: set[int] = set(map(lambda x: x.id, list(user.interested)))
        for interest in interested:
            if interest.id not in interested_ids:
                asyncio.create_task(
                    self.interests_repo.add(
                        user=user, interest=interest, created_by=current_user, slug_type=SlugType.MANAGER
                    )
                )

        await self.user_update(user=user, data=data)
        return user

    def get_user_filters(self, user_id: int) -> dict:
        """Get user filter for agent or represes"""

        current_user_data = self.current_user_data.dict(exclude_none=True)
        filters: dict = dict(id=user_id, type=UserType.CLIENT, **current_user_data)
        return filters

    async def get_current_user(self) -> Optional[User]:
        if self.current_user_data.agency_id:
            agency: Agency = await self.agency_repo.retrieve(
                filters={"id": self.current_user_data.agency_id}, prefetch_fields=['maintainer']
            )
            return agency.maintainer
        if self.current_user_data.agent_id:
            return await self.user_repo.retrieve(filters={"id": self.current_user_data.agent_id})


class UsersInterestGlobalIdCase(UsersInterestCase):
    """
    Добавления интересующих объектов пользователю по global_id
    """

    def __init__(
        self,
        user_repo: Type[UserRepo],
        agency_repo: Type[AgencyRepo],
        interests_repo: Type[UserInterestedRepo],
        property_repo: Type[UserPropertyRepo],
        import_property_service: ImportPropertyService
    ) -> None:
        self.user_repo: UserRepo = user_repo()
        self.user_update = user_changes_logger(
            self.user_repo.update, self, content="Обновление интересов пользователей"
        )
        self.agency_repo: AgencyRepo = agency_repo()
        self.property_repo: UserPropertyRepo = property_repo()
        self.interests_repo: UserInterestedRepo = interests_repo()
        self.import_property_service: ImportPropertyService = import_property_service

    async def __call__(
            self,
            user_id: int,
            interested_global_ids: list[str],
            agent_id: int = None,
            agency_id: int = None
    ) -> User:
        self.init_user_data(agent_id=agent_id, agency_id=agency_id)
        filters: dict[str, Any] = self.get_user_filters(user_id=user_id)
        user: User = await self.user_repo.retrieve(
            filters=filters, prefetch_fields=["interested", "agent"]
        )
        if not user:
            raise UserNotFoundError
        current_user: User = await self.get_current_user()

        interested = []
        for interested_global_id in interested_global_ids:
            interested.append(await self._create_or_update_property(interested_global_id))
        user_interested_ids: set[int] = set(map(lambda x: x.global_id, list(user.interested)))

        for interest in interested:
            if interest.global_id not in user_interested_ids:
                asyncio.create_task(
                    self.interests_repo.add(
                        user=user, interest=interest, created_by=current_user, slug_type=SlugType.MINE
                    )
                )
        return user

    async def _create_or_update_property(self, global_id: str) -> UserProperty:
        """
        Cоздаем или обновляем объект по данным из БД портала
        """
        data = dict(global_id=global_id)
        property = await self.property_repo.retrieve(filters=data)
        if not property:
            property = await self.property_repo.create(data)

        _, updated_property = await self.import_property_service(property=property)
        return updated_property
