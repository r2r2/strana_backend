from google.protobuf.message import DecodeError, Message

from src.core.common.websocket_transport import WSTransport
from src.core.protobuf import pretty_format_pb
from src.exceptions import (
    InvalidMessageStructureError,
    InvalidMessageTypeError,
)
from src.modules.chat.interface import ChatMsgTransportProto
from src.modules.chat.serializers.utils import (
    message_to_type_id,
    type_id_to_message_cls,
)


class ChatWebsocketTransport(WSTransport, ChatMsgTransportProto):
    async def send_message(self, message: Message) -> None:
        await self._send_bytes(message_to_type_id(message).to_bytes() + message.SerializeToString())
        self.logger.debug(f"Sent message {pretty_format_pb(message)}")

    async def get_message(self) -> Message:
        as_bytes = await self._receive_bytes()
        if len(as_bytes) <= 1:
            raise InvalidMessageStructureError("No data received")

        try:
            message_cls = type_id_to_message_cls(as_bytes[0])
            result = message_cls.FromString(as_bytes[1:])
            self.logger.debug(f"Received message {pretty_format_pb(result)}")

        except ValueError as exc:
            raise InvalidMessageTypeError(f"Message type is not registered: {as_bytes[0]}") from exc

        except DecodeError as exc:
            raise InvalidMessageStructureError from exc

        return result
