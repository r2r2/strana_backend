from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator
from sl_messenger_protobuf.enums_pb2 import DeliveryStatus as DeliveryStatusPb

from src.core.common.utility import IntDocEnum
from src.entities.tickets import TicketStatus

MAX_MESSAGE_LENGTH = 5000


class DeliveryStatus(IntDocEnum):
    PENDING = 1
    SENT = 2
    DELIVERED = 3
    READ = 4

    def to_pb(self) -> DeliveryStatusPb.ValueType:
        return DeliveryStatusPb.ValueType(self.value)


class ChatCloseReason(IntDocEnum):
    MAIN_SCOUT_IS_CHANGED = 1
    MATCH_IS_FINISHED = 2
    MEMBERS_INACTIVITY = 3
    INITIATED_BY_USER = 4
    MATCH_IS_CANCELLED = 5


class ChatOpenReason(IntDocEnum):
    INITIATED_BY_USER = 1


class BaseMessageContent(BaseModel):
    def get_referenced_user_ids(self) -> list[int]:
        return []


class ChatClosedNotificationContent(BaseMessageContent):
    reason: ChatCloseReason


class TextContent(BaseMessageContent):
    text: str


class RelatedTicketCreatedNotificationContent(BaseMessageContent):
    ticket_chat_id: int
    ticket_id: int


class ChatCreatedNotificationContent(BaseMessageContent):
    created_by_user_id: int

    def get_referenced_user_ids(self) -> list[int]:
        return [self.created_by_user_id]


class UserJoinedChatNotificationContent(BaseMessageContent):
    user_id: int

    def get_referenced_user_ids(self) -> list[int]:
        return [self.user_id]


class TicketClosedNotificationContent(BaseMessageContent):
    ticket_id: int
    ticket_chat_id: int
    closed_by_user_id: int

    def get_referenced_user_ids(self) -> list[int]:
        return [self.closed_by_user_id]


class UserLeftChatNotificationContent(BaseMessageContent):
    user_id: int

    def get_referenced_user_ids(self) -> list[int]:
        return [self.user_id]


class TicketFirstMessageNotificationContent(BaseMessageContent):
    ticket_id: int
    created_from_chat_id: int | None = None


class TicketStatusChangedNotificationContent(BaseMessageContent):
    ticket_id: int
    status: TicketStatus


class FileContent(BaseMessageContent):
    file_id: str
    filename: str
    size: int
    mime_type: str


class ChatOpenedNotificationContent(BaseMessageContent):
    reason: ChatOpenReason


class UnsupportedContent(BaseMessageContent): ...


class MessageContent(BaseModel):
    unsupported: UnsupportedContent | None = None
    text: TextContent | None = None
    related_ticket_created_notification: RelatedTicketCreatedNotificationContent | None = None
    chat_created_notification: ChatCreatedNotificationContent | None = None
    user_joined_chat_notification: UserJoinedChatNotificationContent | None = None
    ticket_closed_notification: TicketClosedNotificationContent | None = None
    user_left_chat_notification: UserLeftChatNotificationContent | None = None
    ticket_first_message_notification: TicketFirstMessageNotificationContent | None = None
    chat_closed_notification: ChatClosedNotificationContent | None = None
    ticket_status_changed_notification: TicketStatusChangedNotificationContent | None = None
    file: FileContent | None = None
    chat_opened_notification: ChatOpenedNotificationContent | None = None

    def get_referenced_user_ids(self) -> list[int]:
        result = set()

        for _field_name, field_value in self:
            if field_value:
                result.update(field_value.get_referenced_user_ids())

        return list(result)


class Reaction(BaseModel):
    code: str | None = Field(description="Unicode emoji code")
    count: int | None = Field(description="Number of users reacted with this emoji")
    is_user_reacted: bool = Field(False, description="Is user reacted to this message")
    user_ids: list[int] = Field(default_factory=list, description="User ids who reacted with this emoji")


class BaseMessageDTO(BaseModel):
    id: int
    sender_id: int | None
    chat_id: int
    created_at: datetime
    content: MessageContent
    delivery_status: DeliveryStatus
    updated_at: datetime | None
    deleted_at: datetime | None = None
    reactions: list[Reaction] = Field(default_factory=list)


class MessageDTO(BaseMessageDTO):
    reply_to: BaseMessageDTO | None = Field(None, description="Message that this message is a reply to")

    def get_referenced_user_ids(self) -> list[int]:
        referenced = []
        if self.sender_id:
            referenced.append(self.sender_id)

        referenced.extend(self.content.get_referenced_user_ids())
        return referenced

    @model_validator(mode="before")
    @classmethod
    def validate_content(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("deleted_at"):
            values["content"] = MessageContent(text=TextContent(text=""))
        return values
