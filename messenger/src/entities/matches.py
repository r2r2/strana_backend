from dataclasses import dataclass
from datetime import datetime
from enum import unique

from pydantic import BaseModel
from sl_messenger_protobuf.enums_pb2 import ChatType as ChatTypePb

from src.core.common.utility import IntDocEnum
from src.entities.messages import MessageContent


@unique
class ChatType(IntDocEnum):
    PERSONAL = 1
    MATCH = 2
    TICKET = 3

    def to_pb(self) -> ChatTypePb.ValueType:
        return ChatTypePb.ValueType(self.value)


@unique
class MatchState(IntDocEnum):
    ACTIVE = 1
    ARCHIVED = 2
    CANCELLED = 3

    @property
    def is_active(self) -> bool:
        return self == MatchState.ACTIVE


@dataclass
class MatchFilters:
    search_query: str | None = None
    sport_ids: list[int] | None = None
    scout_numbers: list[int] | None = None
    match_date_from: datetime | None = None
    match_date_to: datetime | None = None
    state: MatchState | None = None


@dataclass(repr=True, kw_only=True)
class MatchTeamData:
    id: int
    name_ru: str
    name_en: str


@dataclass(repr=True, kw_only=True, eq=True, frozen=True)
class MatchScoutData:
    id: int
    scout_number: int
    is_main_scout: bool
    name: str


@dataclass(repr=True, kw_only=True, eq=True, frozen=True)
class MatchBasicData:
    start_at: datetime
    finish_at: datetime | None
    sport_id: int
    team_a: MatchTeamData
    team_b: MatchTeamData


@dataclass(repr=True, kw_only=True, eq=True, frozen=True)
class MatchData(MatchBasicData):
    sportlevel_id: int
    scouts: list[MatchScoutData]

    def to_basic_fields(self) -> MatchBasicData:
        return MatchBasicData(
            start_at=self.start_at,
            finish_at=self.finish_at,
            sport_id=self.sport_id,
            team_a=self.team_a,
            team_b=self.team_b,
        )


@dataclass(repr=True, kw_only=True, eq=True, frozen=True)
class MatchDataWithState(MatchData):
    state: MatchState


@dataclass(frozen=True, kw_only=True, eq=True, repr=True)
class MatchUpdatableFields(MatchBasicData): ...


class MatchStoredData(BaseModel):
    sportlevel_id: int
    state: MatchState
    chat_id: int | None = None

    team_a_name: str
    team_b_name: str
    sport_id: int
    sport_name: str
    start_at: datetime

    last_message_created_at: datetime | None = None
    last_message_id: int | None = None
    last_message_content: MessageContent | None = None
    last_message_sender_id: int | None = None

    def get_referenced_user_ids(self) -> list[int]:
        result = set()
        if self.last_message_content:
            result.update(self.last_message_content.get_referenced_user_ids())

        return list(result)
