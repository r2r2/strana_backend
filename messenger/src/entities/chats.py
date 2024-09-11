from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, Field

from src.core.types import UserId
from src.entities.matches import ChatType
from src.entities.messages import MessageContent
from src.entities.users import Role


@dataclass
class ChatMemberDTO:
    user_id: UserId
    user_role: Role


@dataclass
class ChatBaseInfoDTO:
    id: int
    is_closed: bool
    chat_type: ChatType
    primary_members: list[ChatMemberDTO]
    created_at: int


@dataclass(repr=True, frozen=True)
class ChatMembershipDetailsDTO:
    chat_type: ChatType
    is_chat_closed: bool
    is_member: bool
    is_primary_member: bool
    has_write_permission: bool
    user_role: Role | None
    is_archive_member: bool
    last_available_message_id: int | None
    first_available_message_id: int | None


class ChatMeta(BaseModel):
    related_ticket_id: int | None = Field(
        default=None,
        description="ID of the ticket created from this chat. If no tickets were created, this field is null.",
    )
    assigned_ticket_id: int | None = Field(
        default=None,
        description="ID of the ticket assigned to this chat. If no tickets were assigned, this field is null.",
    )


class ChatBaseInfo(BaseModel):
    chat_id: int
    type: ChatType
    is_member: bool
    is_closed: bool
    match_id: int | None
    last_unread_message_id: int | None
    last_message_id: int | None
    last_message_content: MessageContent | None
    last_message_sender_id: int | None
    last_message_created_at: datetime | None
    first_message_id: int | None
    first_message_content: MessageContent | None
    first_message_sender_id: int | None
    first_message_created_at: datetime | None
    last_read_message_id: int | None
    has_write_permission: bool
    meta: ChatMeta


class ChatMemberInfo(BaseModel):
    user_id: int
    is_primary_member: bool
    is_online: bool | None = None
    user_role: str | None = None


class ChatInfo(ChatBaseInfo):
    members: list[ChatMemberInfo] | None = Field(default_factory=list)

    def get_referenced_user_ids(self) -> list[int]:
        referenced = set()
        for member in self.members or []:
            referenced.add(member.user_id)

        if self.last_message_content:
            referenced.update(self.last_message_content.get_referenced_user_ids())

        return list(referenced)
