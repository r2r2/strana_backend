import re
import time
from contextlib import contextmanager
from enum import IntEnum, StrEnum
from typing import Any, Callable, Generator, Iterable, Mapping, Protocol, runtime_checkable

from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema

from src.core.types import LoggerType, T, V


def parse_formatted_pattern(input_string: str, pattern: str) -> dict[str, str]:
    escaped = re.escape(pattern)
    escaped = rf"^{escaped}$"
    regex_pattern = re.sub(r"\\{(.*?)\\}", r"(?P<\1>.*?)", escaped)
    match = re.match(regex_pattern, input_string)
    return match.groupdict() if match else {}


class PatternStrEnum(StrEnum):
    def parse(self, string: str) -> dict[str, str]:
        return parse_formatted_pattern(string, self.value)


@runtime_checkable
class SupportsLifespan(Protocol):
    async def start(self) -> None: ...

    async def stop(self) -> None: ...


@runtime_checkable
class SupportsHealthCheck(Protocol):
    async def health_check(self) -> bool: ...


class IntDocEnum(IntEnum):
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema["enum"] = [f"{choice.name} ({choice.value})" for choice in cls]
        json_schema["type"] = "integer"
        return json_schema


@contextmanager
def time_it(logger: LoggerType, text: str) -> Generator[None, None, None]:
    tstart = time.perf_counter()
    yield
    tend = time.perf_counter()
    logger.debug("Timer result", elapsed=round(tend - tstart, 4), text=text)


def find_by_predicate(data: list[T], predicate: Callable[[T], bool]) -> T | None:
    for item in data:
        if predicate(item):
            return item

    return None


def exclude_fields(inp: Mapping[Any, V], exclude: Iterable[str]) -> dict[str, V]:
    """Exclude the specified fields from dict, returning the new dict"""
    return dict(filter(lambda kv: kv[0] not in exclude, inp.items()))


def pick_fields(inp: Mapping[Any, V], include: Iterable[str]) -> dict[str, V]:
    """Get only specified fields from dict, returning the new dict"""
    return dict(filter(lambda kv: kv[0] in include, inp.items()))
