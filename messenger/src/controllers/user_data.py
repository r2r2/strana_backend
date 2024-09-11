from typing import Any

from fastapi import Depends

from src.api.http.serializers.users import ResponseWithUserData
from src.controllers.users import UsersController
from src.core.types import T
from src.entities.users import AuthPayload, Role, UserData
from src.modules.auth.dependencies import auth_required
from src.modules.users_cache.interface import EntityWithReferencedUsers


class UserDataAdapter:
    def __init__(
        self,
        user: AuthPayload = Depends(auth_required),
        users_controller: UsersController = Depends(),
    ) -> None:
        self.users_controller = users_controller
        self.requested_by = user

    async def enrich_response(
        self,
        response: T,
    ) -> ResponseWithUserData[T]:
        result = ResponseWithUserData(
            data=response,
            user_data=await self._extract_user_data(response),
        )
        self._anonymize_users(result.user_data)
        return result

    async def _extract_user_data(self, response: Any) -> list[UserData]:
        user_ids = set()
        if isinstance(response, EntityWithReferencedUsers):
            user_ids.update(response.get_referenced_user_ids())

        elif isinstance(response, list):
            for item in response:
                if isinstance(item, EntityWithReferencedUsers):
                    user_ids.update(item.get_referenced_user_ids())

        return await self.users_controller.get_users_by_ids(list(user_ids))

    def _anonymize_users(self, user_data: list[UserData]) -> None:
        if self.requested_by.role != Role.SUPERVISOR:
            for user in user_data:
                user.name = ""
