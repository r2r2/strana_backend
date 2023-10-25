from typing import Any

import sentry_sdk


def before_send(event, hint):
    log_entry = event.get("logentry", {})
    message = log_entry.get("message", "")

    # Remove the unwanted string if it exists at the beginning of the message
    unwanted_prefix = "============================================================"
    if message.startswith(unwanted_prefix):
        log_entry["message"] = message[len(unwanted_prefix):]

    return event


async def send_sentry_log(
    tag: str,
    message: str,
    context: dict[str, Any] = None,
    level: str = "info",
) -> None:
    """
    Send a log to Sentry.

    :param tag: Name of the use case.
    :param message: The message to send.
    :param context: The context of the log.
    :param level: The level of the log. Can be "info", "warning" or "error".
    """
    if level not in ("info", "warning", "error"):
        raise ValueError("level must be 'info', 'warning' or 'error'")

    with sentry_sdk.push_scope() as scope:
        scope.set_tag("tag", tag)
        if context:
            [scope.set_extra(key, value) for key, value in context.items()]
        sentry_sdk.capture_message(message, level=level)
