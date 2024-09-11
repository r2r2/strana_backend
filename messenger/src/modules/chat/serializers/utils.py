from typing import Type

from sl_messenger_protobuf.main_pb2 import (
    ClientMessage,
    ServerMessage,
    _sym_db,  # type: ignore[attr-defined]
)
from sl_messenger_protobuf.messages_pb2 import MessageContent

from src.core.types import ProtobufMessage

MessageToTypeMapping = dict[Type[ProtobufMessage], int]
TypeToMessageMapping = dict[int, Type[ProtobufMessage]]


def generate_id_mapping(registry: Type[ProtobufMessage]) -> MessageToTypeMapping:
    """Extracts the type id mapping from the descriptor's oneof message property"""
    return {
        _sym_db.GetSymbol(field.message_type.full_name): field.number
        for field in registry.DESCRIPTOR.oneofs_by_name["message"].fields
    }


_SERVER_MESSAGES_MAPPING = generate_id_mapping(ServerMessage)
_CLIENT_MESSAGES_MAPPING = {v: k for k, v in generate_id_mapping(ClientMessage).items()}


def message_to_type_id(
    message: ProtobufMessage,
    _mapping: MessageToTypeMapping = _SERVER_MESSAGES_MAPPING,
) -> int:
    """Given a protobuf message, returns the corresponding message type id."""
    res = _mapping.get(type(message))
    if not res:
        raise ValueError(f"Type id for message {type(message).__name__} not found")

    return res


def type_id_to_message_cls(
    type_id: int,
    _mapping: TypeToMessageMapping = _CLIENT_MESSAGES_MAPPING,
) -> Type[ProtobufMessage]:
    """Given a message type id, returns the corresponding protobuf message class"""
    res = _mapping.get(type_id)
    if not res:
        raise ValueError(f"Message id not found for type {type_id}")

    return res


def extract_text_content(message: MessageContent) -> str:
    return message.text.text
