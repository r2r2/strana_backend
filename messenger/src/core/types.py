from typing import TYPE_CHECKING, ParamSpec, TypeAlias, TypeVar

from google.protobuf.message import Message as ProtobufMessage
from pydantic import BaseModel
from structlog.types import FilteringBoundLogger

if TYPE_CHECKING:
    from typing import Any  # noqa: F401

    from redis.asyncio import Redis  # noqa: F401


P = ParamSpec("P")
T = TypeVar("T")
V = TypeVar("V")
RetType = TypeVar("RetType")
LoggerType = FilteringBoundLogger
PydanticModel = TypeVar("PydanticModel", bound=BaseModel)
ProtobufMessageT = TypeVar("ProtobufMessageT", bound=ProtobufMessage)
UserId = int
ConnectionId = str
RedisConn: TypeAlias = "Redis[Any]"


__all__ = (
    "ProtobufMessage",
    "ProtobufMessageT",
    "T",
    "P",
    "RetType",
    "LoggerType",
    "PydanticModel",
    "UserId",
    "ConnectionId",
    "RedisConn",
)
