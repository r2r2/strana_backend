from typing import Protocol

from src.entities.matches import MatchScoutData
from src.entities.users import Role
from src.modules.storage.models.user import User


class SportlevelUsersSyncManagerProto(Protocol):
    async def run_users_sync(self) -> None: ...

    async def sync_user_from_sl(self, user: MatchScoutData, role: Role) -> None: ...

    async def sync_user_from_db(self, user: User) -> None: ...
