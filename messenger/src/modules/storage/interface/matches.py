from typing import Protocol

from src.core.types import UserId
from src.entities.matches import (
    MatchDataWithState,
    MatchFilters,
    MatchScoutData,
    MatchState,
    MatchStoredData,
    MatchUpdatableFields,
)
from src.entities.users import Language, Role
from src.modules.storage.models.match import MatchScout


class MatchOperationsProtocol(Protocol):
    async def get_match_by_id(self, sportlevel_id: int) -> MatchDataWithState | None: ...

    async def create_match_with_scouts(self, match_data: MatchDataWithState) -> None: ...

    async def update_match(self, sportlevel_id: int, updates: MatchUpdatableFields) -> None: ...

    async def update_match_state(self, sportlevel_id: int, state: MatchState) -> None: ...

    async def get_match_scouts(self, match_id: int) -> list[MatchScoutData]: ...

    async def get_match_scout(self, match_id: int, scout_id: int) -> MatchScout | None: ...

    async def set_match_scouts(self, match_id: int, scouts: list[MatchScoutData]) -> None: ...

    async def get_match_info(
        self,
        user_id: UserId,
        user_role: Role,
        lang: Language,
        match_id: int,
    ) -> MatchStoredData | None: ...

    async def get_matches(
        self,
        user_id: UserId,
        user_role: Role,
        lang: Language,
        filters: MatchFilters,
        limit: int,
        offset: int,
    ) -> list[MatchStoredData]: ...

    async def get_matches_list(
        self,
        user_id: UserId,
        user_role: Role,
        lang: Language,
        filters: MatchFilters,
        limit: int,
        offset: int,
    ) -> list[MatchStoredData]: ...

    async def get_all_users_related_to_match(self, match_id: int) -> list[int]:
        """
        Get all users related to match (scouts, bookmakers, etc.)
        i.e. users who have chats within this match, including ticket chats
        """
        ...

    async def delete_match_with_scouts(self, match_id: int) -> None:
        """
        Delete match and match scouts connected to it
        """
