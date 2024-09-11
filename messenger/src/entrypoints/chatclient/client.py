from uuid import uuid4

from sl_messenger_protobuf.main_pb2 import ClientMessage, ServerMessage
from sl_messenger_protobuf.messages_pb2 import MessageContent, TextContent
from sl_messenger_protobuf.requests_pb2 import (
    MessageReadCommand,
    MessageReceivedCommand,
    SendActivityCommand,
    SendMessageCommand,
)
from websockets.client import WebSocketClientProtocol

from src.core.protobuf import pretty_format_pb
from src.core.types import LoggerType, ProtobufMessage
from src.modules.chat.serializers.utils import (
    generate_id_mapping,
    message_to_type_id,
    type_id_to_message_cls,
)
from src.providers.time import timestamp_now

_CLIENT_REQUESTS_MAPPING = generate_id_mapping(ClientMessage)
_SERVER_RESPONSES_MAPPING = {v: k for k, v in generate_id_mapping(ServerMessage).items()}


class ChatTestClient:
    def __init__(
        self,
        logger: LoggerType,
        conn: WebSocketClientProtocol,
    ) -> None:
        self.conn = conn
        self.logger = logger

    async def receive_message(self) -> ProtobufMessage:
        raw = await self.conn.recv()
        assert isinstance(raw, bytes)
        message_cls = type_id_to_message_cls(raw[0], _SERVER_RESPONSES_MAPPING)

        result = message_cls.FromString(raw[1:])
        self.logger.debug(f"Received message {pretty_format_pb(result)}")
        return result

    async def send_text_message(self, text: str, chat_id: int) -> None:
        cmd = SendMessageCommand(
            temporary_id=uuid4().bytes,
            chat_id=chat_id,
            content=MessageContent(text=TextContent(text=text)),
        )
        await self._send_message(cmd)

    async def send_activity(self, chat_id: int | None, is_typing: bool) -> None:
        activity = SendActivityCommand(created_at=timestamp_now())
        if chat_id:
            activity.chat_id = chat_id
            activity.is_typing = is_typing

        await self._send_message(activity)

    async def send_message_read(self, message_id: int) -> None:
        await self._send_message(MessageReadCommand(message_id=message_id))

    async def send_message_received(self, message_id: int) -> None:
        await self._send_message(MessageReceivedCommand(message_id=message_id))

    async def _send_message(self, message: ProtobufMessage) -> None:
        await self.conn.send(
            message_to_type_id(message, _CLIENT_REQUESTS_MAPPING).to_bytes() + message.SerializeToString(),
        )
        self.logger.debug(f"Sent message {pretty_format_pb(message)}")
