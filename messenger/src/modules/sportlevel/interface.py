from datetime import datetime
from enum import Enum
from typing import AsyncGenerator, Protocol

from sl_api_client.serializers.users import UserResponse

from src.core.common.utility import SupportsHealthCheck, SupportsLifespan
from src.entities.matches import MatchDataWithState, MatchState
from src.entities.users import Language
from src.exceptions import InternalError
from src.modules.sportlevel.settings import SportlevelSettings


class SLMatchState(int, Enum):
    ANNOUNCE = 1
    STARTING = 2
    LIVE = 3
    STOPPING = 4
    ARCHIVE = 5
    CANCELLED = 6
    DRAFT = 7

    def to_match_state(self) -> MatchState:
        match self.value:
            case 1 | 2 | 3 | 4 | 7:
                return MatchState.ACTIVE
            case 5:
                return MatchState.ARCHIVED
            case 6:
                return MatchState.CANCELLED
            case _:
                raise InternalError(f"Unknown sportlevel state id: {self}")


class SportlevelServiceProto(SupportsLifespan, SupportsHealthCheck, Protocol):
    settings: SportlevelSettings

    async def change_language(self, user_id: int, lang: Language) -> bool: ...

    async def get_match_by_id(self, match_id: int) -> MatchDataWithState | None: ...

    async def get_user_by_id(self, user_id: int) -> UserResponse | None: ...

    async def iter_matches(
        self,
        date_from: datetime,
        date_to: datetime,
        state_id: int | None = None,
    ) -> AsyncGenerator[MatchDataWithState, None]: ...
