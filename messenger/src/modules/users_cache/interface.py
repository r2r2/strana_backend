from typing import Protocol, runtime_checkable

from src.core.common.utility import SupportsLifespan
from src.entities.users import UserData


@runtime_checkable
class EntityWithReferencedUsers(Protocol):
    def get_referenced_user_ids(self) -> list[int]: ...


class UsersCacheProtocol(SupportsLifespan, Protocol):
    async def get(self, user_id: int) -> UserData | None: ...

    async def set(self, user_id: int, data: UserData) -> None:  # noqa: A003
        ...

    async def get_multiple(self, user_ids: list[int]) -> dict[int, UserData]: ...

    async def set_multiple(self, data: dict[int, UserData]) -> None: ...
