from typing import Any

from src.core.types import ProtobufMessage


def pretty_format_pb(message: ProtobufMessage | Any) -> str:
    """Returns a pretty formatted string representation of the protobuf message"""
    if not isinstance(message, ProtobufMessage):
        return str(message)

    msg_fields = ",".join(f"{descriptor.name}={pretty_format_pb(value)}" for descriptor, value in message.ListFields())
    return f"{type(message).__name__}({msg_fields})"
