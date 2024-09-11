from fastapi import Depends, HTTPException, status

from src.core.di import Injected
from src.entities.users import Ability, AuthPayload, Role, UserData
from src.modules.auth.interface import AuthServiceProto
from src.modules.sportlevel.interface import SportlevelServiceProto
from src.modules.storage.dependencies import inject_storage
from src.modules.storage.interface import StorageProtocol
from src.modules.users_cache import UsersCacheProtocol


class UsersController:
    def __init__(
        self,
        auth: AuthServiceProto = Injected[AuthServiceProto],
        users_cache: UsersCacheProtocol = Injected[UsersCacheProtocol],
        sportlevel: SportlevelServiceProto = Injected[SportlevelServiceProto],
        storage: StorageProtocol = Depends(inject_storage),
    ) -> None:
        self.auth = auth
        self.storage = storage
        self.sportlevel = sportlevel
        self._cache = users_cache

    async def sync_user_roles(self, user: AuthPayload) -> None:
        if len(user.roles) > 1:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "User has more than one role, please contact the support to resolve the issue.",
            )

        db_user = await self.storage.users.get_by_id(user.id)
        if not db_user:
            # Create user with role from token
            sl_user_info = await self.sportlevel.get_user_by_id(user.id)
            if not sl_user_info:
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Error retrieving user info from Sportlevel",
                )

            await self.storage.users.create(
                user_id=user.id,
                name=sl_user_info.name,
                scout_number=sl_user_info.scout_num,
                role=user.role,
            )

        elif db_user.role != user.role and user.role != Role.SCOUT:
            # Update role
            await self.storage.users.update_role(
                user_id=user.id,
                role=user.role,
            )

    async def search_users(
        self,
        exclude_user_id: int | None,
        filter_by_role: Role | None,
        query: str | None,
        offset: int,
        limit: int,
    ) -> tuple[list[UserData], int]:
        users, total_count = await self.storage.users.search(
            exclude_user_id=exclude_user_id,
            search_string=query,
            filter_by_role=filter_by_role,
            limit=limit,
            offset=offset,
            exclude_roles=[Role.SUPERVISOR] if not filter_by_role else [],
        )
        return [
            UserData(
                id=user.sportlevel_id,
                name=user.name,
                scout_number=user.scout_number,
                role=user.role,
            )
            for user in users
        ], total_count

    async def get_user_by_id(self, user_id: int) -> UserData | None:
        if cached := await self._cache.get(user_id):
            return cached

        if not (user := await self.storage.users.get_by_id(user_id)):
            return None

        user_data = UserData(
            id=user.sportlevel_id,
            role=user.role,
            name=user.name,
            scout_number=user.scout_number,
        )
        await self._cache.set(user_id, user_data)
        return user_data

    async def get_users_by_ids(self, user_ids: list[int]) -> list[UserData]:
        cached = await self._cache.get_multiple(user_ids)
        if len(cached) != len(user_ids):
            missing = set(user_ids) - set(cached)
            users = await self.storage.users.get_by_ids(list(missing))
            cache_updates = {
                user.sportlevel_id: UserData(
                    id=user.sportlevel_id,
                    role=user.role,
                    name=user.name,
                    scout_number=user.scout_number,
                )
                for user in users
            }
            await self._cache.set_multiple(cache_updates)

            return [
                *cached.values(),
                *[item.copy() for item in cache_updates.values()],
            ]

        return list(cached.values())

    async def grant_ability(self, user_id: int, ability: Ability) -> None:
        await self.auth.grant(user_id, ability.value)

    async def grant_role(self, user_id: int, role: Role) -> None:
        self._check_protected_role(role)
        user = await self.storage.users.get_by_id(user_id)
        if user:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "User with this id already exists",
            )

        user_info = await self.sportlevel.get_user_by_id(user_id)
        if not user_info:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "User with this id does not exist",
            )

        await self.storage.users.create(
            user_id=user_id,
            name=user_info.name,
            scout_number=user_info.scout_num,
            role=role,
        )
        await self.auth.grant(user_id, role.value)

    async def revoke_role(self, user_id: int, role: Role) -> None:
        self._check_protected_role(role)
        user = await self.storage.users.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "User with this id does not exist",
            )

        await self.auth.revoke(user_id, role)

    def _check_protected_role(self, role: Role) -> None:
        if role == Role.SCOUT:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Scout role cannot be modified manually")
