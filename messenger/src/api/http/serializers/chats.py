from pydantic import BaseModel, Field

from src.entities.chats import ChatInfo
from src.entities.matches import ChatType


class CreateChatRequest(BaseModel):
    target_user_id: int


class CreateChatResponse(BaseModel):
    chat_id: int


class UnreadCountResponse(BaseModel):
    unread: int


class ChatUnreadCountersResponse(BaseModel):
    total: int
    by_chat_type: dict[ChatType, int]


class OptionsScoutResponse(BaseModel):
    user_id: int
    is_main_scout: bool


class OptionsExistingChatResponse(BaseModel):
    user_id: int
    chat_id: int


class ChatOptionsResponse(BaseModel):
    current_scouts: list[OptionsScoutResponse] = Field(default_factory=list)
    existing_chats: list[OptionsExistingChatResponse] = Field(default_factory=list)
    available_chats: list[int] = Field(default_factory=list)

    def get_referenced_user_ids(self) -> list[int]:
        curr_scouts = {scout.user_id for scout in self.current_scouts}
        all_chats_with_scouts = {chat.user_id for chat in self.existing_chats}

        return list(curr_scouts.union(all_chats_with_scouts))


class ChatResponse(ChatInfo):
    unread_count: int
