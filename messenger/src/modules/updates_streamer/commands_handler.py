from typing import TYPE_CHECKING, Any, Awaitable, Callable

from google.protobuf.message import DecodeError
from sl_messenger_protobuf.updates_streamer_pb2 import (
    StreamerClientRequest,
    StreamerUpdate,
    SubscribeRequest,
    UnreadCountersUpdate,
    UnsubscribeRequest,
)

from src.controllers.unread_counters import UnreadCountersController
from src.core.protobuf import pretty_format_pb
from src.modules.updates_streamer.entities import ConnectionInfo

if TYPE_CHECKING:
    from src.modules.updates_streamer.controller import StreamerWebsocketHandler


async def handle_subscribe(
    ctx: "StreamerWebsocketHandler",
    command: SubscribeRequest,
    connection: ConnectionInfo,
) -> None:
    ctx.logger.debug("Subscribe request", command=pretty_format_pb(command))
    async with ctx._storage.connect() as db_conn:
        connection.online_user_ids.update(command.user_ids)

        for user_id in command.user_ids:
            await ctx.subscriptions.add_sub(user_id)

            controller = UnreadCountersController(
                settings=ctx.settings.unread_counters,
                storage=db_conn,
            )

            unread_count = await controller.get_total_unread_count(user_id=user_id)

            ctx.logger.debug(
                f"Total unread count: {unread_count}",
                user_id=user_id,
            )

            await connection.transport.send_message(
                StreamerUpdate(
                    unread_counters_update=UnreadCountersUpdate(user_id=user_id, unread_count=int(unread_count))
                )
            )


async def handle_unsubscribe(
    ctx: "StreamerWebsocketHandler",
    command: UnsubscribeRequest,
    connection: ConnectionInfo,
) -> None:
    ctx.logger.debug("Unsubscribe request", command=pretty_format_pb(command))
    connection.online_user_ids.difference_update(command.user_ids)

    for user_id in command.user_ids:
        await ctx.subscriptions.remove_sub(user_id)


handlers: dict[str, Callable[..., Awaitable[Any]]] = {
    "subscribe_request": handle_subscribe,
    "unsubscribe_request": handle_unsubscribe,
}


async def handle_client_command(
    ctx: "StreamerWebsocketHandler",
    command: bytes,
    connection: ConnectionInfo,
) -> None:
    try:
        parsed = StreamerClientRequest.FromString(command)
        message_type_str = parsed.WhichOneof("message")

        if not message_type_str:
            ctx.logger.error("Empty message", command_bytes=command)
            return

        if not (handler := handlers.get(message_type_str)):
            ctx.logger.critical("Unknown message type", message_type=message_type_str)
            return

        await handler(ctx, getattr(parsed, message_type_str), connection)

    except DecodeError:
        ctx.logger.error("Invalid command structure", command_bytes=command)
        return
