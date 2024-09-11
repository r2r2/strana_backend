from typing import Any, Type, overload

from sl_messenger_protobuf.messages_pb2 import MessageContent as MessageContentPb
from sqlalchemy.orm import DeclarativeBase, MappedColumn

from src.entities.messages import (
    ChatClosedNotificationContent,
    ChatCreatedNotificationContent,
    ChatOpenedNotificationContent,
    FileContent,
    MessageContent,
    RelatedTicketCreatedNotificationContent,
    TextContent,
    TicketClosedNotificationContent,
    TicketFirstMessageNotificationContent,
    TicketStatusChangedNotificationContent,
    UnsupportedContent,
    UserJoinedChatNotificationContent,
    UserLeftChatNotificationContent,
)
from src.entities.users import Language
from src.modules.chat.serializers.converters import pb_to_chat_close_reason, pb_to_chat_open_reason, pb_to_ticket_status

DEFAULT_LANG = Language.RU


def get_localized_column(
    object_: DeclarativeBase | Type[DeclarativeBase],
    attr_name: str,
    lang: Language,
    default_attr_name: str | None = None,
) -> MappedColumn[Any]:
    if not default_attr_name:
        default_attr_name = attr_name

    return getattr(
        object_,
        f"{attr_name}_{lang.value}",
        getattr(object_, f"{default_attr_name}_{DEFAULT_LANG.value}"),
    )


@overload
def parse_message_content(raw_content: bytes) -> MessageContent: ...


@overload
def parse_message_content(raw_content: None) -> None: ...


def parse_message_content(raw_content: bytes | None) -> MessageContent | None:
    if raw_content is None:
        return None

    content = MessageContentPb.FromString(raw_content)
    match content.WhichOneof("content"):
        case "text":
            return MessageContent(text=TextContent(text=content.text.text))

        case "related_ticket_created_notification":
            return MessageContent(
                related_ticket_created_notification=RelatedTicketCreatedNotificationContent(
                    ticket_chat_id=content.related_ticket_created_notification.ticket_chat_id,
                    ticket_id=content.related_ticket_created_notification.ticket_id,
                ),
            )

        case "user_joined_chat_notification":
            return MessageContent(
                user_joined_chat_notification=UserJoinedChatNotificationContent(
                    user_id=content.user_joined_chat_notification.user_id,
                ),
            )

        case "chat_created_notification":
            return MessageContent(
                chat_created_notification=ChatCreatedNotificationContent(
                    created_by_user_id=content.chat_created_notification.created_by_user_id,
                ),
            )

        case "ticket_closed_notification":
            return MessageContent(
                ticket_closed_notification=TicketClosedNotificationContent(
                    closed_by_user_id=content.ticket_closed_notification.closed_by_user_id,
                    ticket_chat_id=content.ticket_closed_notification.ticket_chat_id,
                    ticket_id=content.ticket_closed_notification.ticket_id,
                ),
            )

        case "user_left_chat_notification":
            return MessageContent(
                user_left_chat_notification=UserLeftChatNotificationContent(
                    user_id=content.user_left_chat_notification.user_id,
                ),
            )

        case "ticket_first_message_notification":
            return MessageContent(
                ticket_first_message_notification=TicketFirstMessageNotificationContent(
                    ticket_id=content.ticket_first_message_notification.ticket_id,
                    created_from_chat_id=content.ticket_first_message_notification.created_from_chat_id,
                ),
            )

        case "chat_closed_notification":
            return MessageContent(
                chat_closed_notification=ChatClosedNotificationContent(
                    reason=pb_to_chat_close_reason(content.chat_closed_notification.reason),
                ),
            )

        case "ticket_status_changed_notification":
            return MessageContent(
                ticket_status_changed_notification=TicketStatusChangedNotificationContent(
                    ticket_id=content.ticket_status_changed_notification.ticket_id,
                    status=pb_to_ticket_status(content.ticket_status_changed_notification.status),
                ),
            )

        case "file":
            return MessageContent(
                file=FileContent(
                    file_id=content.file.file_id,
                    filename=content.file.filename,
                    size=content.file.size,
                    mime_type=content.file.mime_type,
                ),
            )

        case "chat_opened_notification":
            return MessageContent(
                chat_opened_notification=ChatOpenedNotificationContent(
                    reason=pb_to_chat_open_reason(content.chat_opened_notification.reason),
                ),
            )

        case _:
            return MessageContent(unsupported=UnsupportedContent())
