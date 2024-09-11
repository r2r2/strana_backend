from typing import Any

import pytest

from src.entities.redis import PatternStrEnum, RedisPubSubChannelName, UnreadCountCacheKey


class PatternTestEnum(PatternStrEnum):
    A = "Message with template, with args {arg_a} and {arg_b} = {arg_c}"
    B = "More complex example of formatting: {a}/{b}-{d} ({c})"
    C = "{arg_a} at the start"
    D = "at the end {arg_a}"


@pytest.mark.parametrize(
    argnames=["enum", "format_args"],
    argvalues=[
        (RedisPubSubChannelName.CONNECTION_UPDATES, {"connection_id": 5}),
        (UnreadCountCacheKey.BY_CHAT, {"user_id": 1, "chat_id": 2}),
        (UnreadCountCacheKey.BY_MATCH, {"user_id": 3, "match_id": 4}),
        (UnreadCountCacheKey.BY_CHAT_TYPE, {"user_id": 5, "chat_type": "group"}),
        (UnreadCountCacheKey.TOTAL, {"user_id": 6}),
        (RedisPubSubChannelName.CONNECTION_UPDATES, {"connection_id": 7}),
        (RedisPubSubChannelName.UNREAD_COUNTERS_UPDATES, {"user_id": 8}),
        (PatternTestEnum.A, {"arg_a": 1, "arg_b": 2, "arg_c": 3}),
        (PatternTestEnum.B, {"a": 1, "b": 2, "c": 3, "d": 4}),
        (PatternTestEnum.C, {"arg_a": 1}),
        (PatternTestEnum.D, {"arg_a": 1}),
    ],
)
@pytest.mark.unit
def test_smth(
    enum: PatternStrEnum,
    format_args: dict[str, Any],
) -> None:
    serialized = enum.format(**format_args)
    deserialized = enum.parse(serialized)
    assert deserialized == {key: str(value) for key, value in format_args.items()}
