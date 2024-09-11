from enum import auto
from typing import Literal

from pydantic import BaseModel, Field, RootModel

from src.core.common import StringEnum
from src.core.types import ConnectionId, UserId
from src.entities.matches import ChatType, MatchBasicData, MatchDataWithState, MatchScoutData, MatchState
from src.entities.messages import DeliveryStatus
from src.entities.tickets import TicketStatus
from src.entities.users import PresenceStatus, Role
from src.providers.time import timestamp_now


class ServiceUpdateType(StringEnum):
    MESSAGE_SENT = auto()
    DELIVERY_STATUS_CHANGED = auto()
    PRESENCE_STATUS_CHANGED = auto()
    USER_IS_TYPING = auto()
    MATCH_CREATED = auto()
    MATCH_DATA_CHANGED = auto()
    MATCH_STATE_CHANGED = auto()
    MATCH_SCOUTS_CHANGED = auto()
    USER_DATA_CHANGED = auto()
    TICKET_CREATED = auto()
    TICKET_STATUS_CHANGED = auto()
    CHAT_CREATED = auto()
    REACTION_UPDATED = auto()
    MESSAGE_EDITED = auto()
    MESSAGE_DELETED = auto()


class ServiceUpdate(BaseModel):
    type: ServiceUpdateType
    created_at: int = Field(default_factory=timestamp_now)
    cid: ConnectionId | None = None


class MessageSentToChat(ServiceUpdate):
    type: Literal[ServiceUpdateType.MESSAGE_SENT] = ServiceUpdateType.MESSAGE_SENT  # type: ignore
    initiator_id: int | None = None
    message_id: int
    sender_id: int | None = None
    chat_id: int
    content_raw: str
    msg_created_at: int
    do_not_increment_counter: bool = False


class DeliveryStatusChanged(ServiceUpdate):
    type: Literal[ServiceUpdateType.DELIVERY_STATUS_CHANGED] = ServiceUpdateType.DELIVERY_STATUS_CHANGED  # type: ignore
    message_id: int
    chat_id: int
    user_id: UserId
    status: DeliveryStatus
    updated_for_user: int
    updated_for_all: int


class PresenceStatusChanged(ServiceUpdate):
    type: Literal[ServiceUpdateType.PRESENCE_STATUS_CHANGED] = ServiceUpdateType.PRESENCE_STATUS_CHANGED  # type: ignore
    user_id: UserId
    status: PresenceStatus


class UserIsTypingMessage(ServiceUpdate):
    type: Literal[ServiceUpdateType.USER_IS_TYPING] = ServiceUpdateType.USER_IS_TYPING  # type: ignore
    chat_id: int
    user_id: UserId
    is_typing: bool


class MatchCreated(ServiceUpdate):
    type: Literal[ServiceUpdateType.MATCH_CREATED] = ServiceUpdateType.MATCH_CREATED  # type: ignore
    payload: MatchDataWithState


class MatchDataChanged(ServiceUpdate):
    type: Literal[ServiceUpdateType.MATCH_DATA_CHANGED] = ServiceUpdateType.MATCH_DATA_CHANGED  # type: ignore
    sportlevel_id: int
    fields: MatchBasicData


class MatchStateChanged(ServiceUpdate):
    type: Literal[ServiceUpdateType.MATCH_STATE_CHANGED] = ServiceUpdateType.MATCH_STATE_CHANGED  # type: ignore
    sportlevel_id: int
    old_state: MatchState
    new_state: MatchState


class MatchScoutsChanged(ServiceUpdate):
    type: Literal[ServiceUpdateType.MATCH_SCOUTS_CHANGED] = ServiceUpdateType.MATCH_SCOUTS_CHANGED  # type: ignore
    sportlevel_id: int
    scouts: list[MatchScoutData]


class UserDataChanged(ServiceUpdate):
    type: Literal[ServiceUpdateType.USER_DATA_CHANGED] = ServiceUpdateType.USER_DATA_CHANGED  # type: ignore
    user_id: int
    scout_number: int | None
    name: str
    role: Role


class TicketCreated(ServiceUpdate):
    type: Literal[ServiceUpdateType.TICKET_CREATED] = ServiceUpdateType.TICKET_CREATED  # type: ignore
    created_by_user_id: int
    ticket_id: int
    match_id: int | None
    chat_id: int


class TicketStatusChanged(ServiceUpdate):
    type: Literal[ServiceUpdateType.TICKET_STATUS_CHANGED] = ServiceUpdateType.TICKET_STATUS_CHANGED  # type: ignore
    changed_by_user_id: int
    ticket_id: int
    old_status: TicketStatus
    new_status: TicketStatus


class ChatCreated(ServiceUpdate):
    type: Literal[ServiceUpdateType.CHAT_CREATED] = ServiceUpdateType.CHAT_CREATED  # type: ignore
    chat_id: int
    chat_type: ChatType
    created_by_user_id: int | None
    match_id: int | None


class ReactionUpdatedMessage(ServiceUpdate):
    type: Literal[ServiceUpdateType.REACTION_UPDATED] = ServiceUpdateType.REACTION_UPDATED  # type: ignore
    message_id: int
    user_id: int
    emoji: str
    emoji_count: int
    chat_id: int
    is_deleted: bool


class MessageEdited(ServiceUpdate):
    type: Literal[ServiceUpdateType.MESSAGE_EDITED] = ServiceUpdateType.MESSAGE_EDITED  # type: ignore
    message_id: int
    chat_id: int
    content_raw: str


class MessageDeleted(ServiceUpdate):
    type: Literal[ServiceUpdateType.MESSAGE_DELETED] = ServiceUpdateType.MESSAGE_DELETED  # type: ignore
    message_id: int
    chat_id: int


AnyUpdate = (
    MessageSentToChat
    | DeliveryStatusChanged
    | PresenceStatusChanged
    | UserIsTypingMessage
    | MatchCreated
    | MatchDataChanged
    | MatchStateChanged
    | MatchScoutsChanged
    | UserDataChanged
    | TicketCreated
    | TicketStatusChanged
    | ChatCreated
    | ReactionUpdatedMessage
    | MessageEdited
    | MessageDeleted
)


IncomingServiceUpdateModel = RootModel[AnyUpdate]
