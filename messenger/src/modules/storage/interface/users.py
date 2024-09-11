from typing import Protocol

from src.core.types import UserId
from src.entities.users import Role
from src.modules.storage.models.user import User


class UserOperationsProtocol(Protocol):
    async def search(
        self,
        exclude_user_id: int | None = None,
        search_string: str | None = None,
        filter_by_role: Role | None = None,
        limit: int | None = None,
        offset: int | None = None,
        exclude_roles: list[Role] | None = None,
    ) -> tuple[list[User], int]: ...

    async def get_by_ids(self, user_ids: list[UserId]) -> list[User]: ...

    async def get_by_id(self, user_id: UserId) -> User | None: ...

    async def create(
        self,
        user_id: UserId,
        name: str,
        scout_number: int | None,
        role: Role,
    ) -> None: ...

    async def update(
        self,
        user_id: UserId,
        name: str,
        scout_number: int | None,
        role: Role | None = None,
    ) -> None: ...

    async def update_role(self, role: Role, user_id: UserId) -> None: ...
