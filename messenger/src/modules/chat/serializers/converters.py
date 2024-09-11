from sl_messenger_protobuf.enums_pb2 import ChatCloseReason as ChatCloseReasonPb2
from sl_messenger_protobuf.enums_pb2 import ChatOpenReason as ChatOpenReasonPb2
from sl_messenger_protobuf.enums_pb2 import TicketStatus as TicketStatusPb2
from sl_messenger_protobuf.enums_pb2 import UserRole as UserRolePb2

from src.entities.messages import ChatCloseReason, ChatOpenReason
from src.entities.tickets import TicketStatus
from src.entities.users import Role


def pb_to_chat_close_reason(pb_reason: ChatCloseReasonPb2.ValueType) -> ChatCloseReason:
    return ChatCloseReason(pb_reason)


def pb_to_chat_open_reason(pb_reason: ChatOpenReasonPb2.ValueType) -> ChatOpenReason:
    return ChatOpenReason(pb_reason)


def pb_to_ticket_status(pb_status: TicketStatusPb2.ValueType) -> TicketStatus:
    return TicketStatus(pb_status)


def ticket_status_to_pb(status: TicketStatus) -> TicketStatusPb2.ValueType:
    return TicketStatusPb2.ValueType(status.value)


def role_to_pb(status: Role) -> UserRolePb2.ValueType:
    match status:
        case Role.SCOUT:
            return UserRolePb2.USER_ROLE_SCOUT
        case Role.BOOKMAKER:
            return UserRolePb2.USER_ROLE_BOOKMAKER
        case Role.SUPERVISOR:
            return UserRolePb2.USER_ROLE_SUPERVISOR
        case _:
            raise ValueError(f"Cannot cast role to pb: {status}")
