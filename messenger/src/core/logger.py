from enum import auto, unique
from typing import Any, MutableMapping, cast

from boilerplates.logging import ChainBuilder
from boilerplates.logging import get_logger as bp_get_logger
from boilerplates.logging import setup_logging as _setup_logging
from starlette_context import context
from structlog.types import EventDict, FilteringBoundLogger, WrappedLogger

from src.core.common import StringEnum
from src.core.settings import LoggingSettings


@unique
class LoggerName(StringEnum):
    ROOT = ""
    AUTH = auto()
    ACCESS = auto()
    WS = auto()
    TESTS = auto()
    CONNECTIONS_REGISTRY = auto()
    CONNECTION = auto()
    PRESENCE = auto()
    MESSAGE_HANDLER = auto()
    UPDATES_LISTENER = auto()
    RMQ_PUBLISHER = auto()
    PUBSUB = auto()
    MIGRATION = auto()
    SL = auto()
    SL_SYNC = auto()
    PERIODIC_TASKS = auto()
    USERS_CACHE = auto()
    JOB_AUTOCLOSE_PRIVATE_CHATS = auto()
    MATCH_STATE_UPDATES_LISTENER = auto()
    MATCH_SCOUT_CHANGES_LISTENER = auto()
    COUNTERS_STREAMER = auto()
    CACHER = auto()
    PUSH_SENDER = auto()
    PUSH_LISTENER = auto()
    PUSH_PUBLISHER = auto()
    TELEGRAM = auto()


def add_extra_context(logger: WrappedLogger, name: str, event_dict: EventDict) -> EventDict:
    """Add information from the global context to the event_dict"""
    event_dict.update(**get_log_ctx())
    return event_dict


def add_to_log_ctx(**data: Any) -> None:
    context.update(**data)


def get_log_ctx() -> MutableMapping[str, Any]:
    if not context.exists():
        return {}

    return context


def get_connection_id() -> str:
    if not (cid := get_log_ctx().get("cid", None)):
        raise RuntimeError("Incorrect usage: outside of the request context")

    return cast(str, cid)


def setup_logging(settings: LoggingSettings, is_sentry_enabled: bool) -> None:
    chain = (
        ChainBuilder.create_default_preset(is_sentry_enabled=is_sentry_enabled)
        .add(add_extra_context, "add_starlette_context", append_after=None)
        .build()
    )
    _setup_logging(
        log_format=settings.log_format,
        log_level=settings.log_level,
        is_sentry_enabled=is_sentry_enabled,
        clear_existing_handlers=True,
        spammy_loggers=settings.spammy_loggers,
        processors_chain=chain,
    )


def get_logger(name: LoggerName | str = "root", *args: Any, **kwargs: Any) -> FilteringBoundLogger:
    if isinstance(name, LoggerName):
        return bp_get_logger(name.name.lower(), *args, **kwargs)

    return bp_get_logger(name.lower(), *args, **kwargs)


__all__ = (
    "get_logger",
    "add_to_log_ctx",
    "get_log_ctx",
)
