from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol, Self

from src.core.common import SupportsHealthCheck
from src.core.types import UserId
from src.entities.users import Role


@dataclass(repr=True, kw_only=True)
class PackedUserData:
    user_id: UserId
    role: Role

    def pack(self) -> str:
        return f"{self.user_id}:{self.role.value}"

    @classmethod
    def unpack(cls, packed: str) -> Self:
        user_id, role = packed.split(":")
        return cls(user_id=int(user_id), role=Role(role))


class PresenceServiceProto(SupportsHealthCheck, Protocol):
    async def set_user_is_active(self, user_id: UserId, role: Role) -> None: ...

    async def set_user_using_chat(self, user_id: UserId, role: Role, chat_id: int) -> None: ...

    async def get_active_users_in_chats(
        self,
        chat_ids: list[int],
        activity_time: timedelta | None = None,
    ) -> list[PackedUserData]: ...

    async def get_active_users(
        self,
        filter_by_role: Role | None = None,
        activity_time: timedelta | None = None,
    ) -> list[PackedUserData]: ...
