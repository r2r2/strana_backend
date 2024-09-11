import asyncio
from typing import Any, Awaitable, Callable, Type, Union

from httpx import AsyncClient
from sl_messenger_protobuf.enums_pb2 import (
    DeliveryStatus,
    UserStatus,
)
from sl_messenger_protobuf.responses_pb2 import (
    DeliveryStatusChangedUpdate,
    MessageReceivedUpdate,
    MessageSentUpdate,
    UserIsTypingUpdate,
    UserStatusChangedUpdate,
)
from websockets.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosed

from src.core.types import LoggerType, ProtobufMessage, UserId
from src.entrypoints.chatclient.client import ChatTestClient
from src.modules.chat.serializers.utils import extract_text_content
from src.providers.time import datetime_now

AnyHandler = Callable[..., Awaitable[Any]]


def render_msg_status(update: Union[DeliveryStatus, int]) -> str:
    mapping: dict[DeliveryStatus | int, str] = {
        DeliveryStatus.DELIVERY_STATUS_UNSPECIFIED: "✗",
        DeliveryStatus.DELIVERY_STATUS_SENT: ".",
        DeliveryStatus.DELIVERY_STATUS_READ: "✓✓",
        DeliveryStatus.DELIVERY_STATUS_PENDING: "⏲",
        DeliveryStatus.DELIVERY_STATUS_DELIVERED: "✓",
    }
    return mapping.get(update, "⁉️")


class InteractiveChatClient(ChatTestClient):
    def __init__(
        self,
        logger: LoggerType,
        user_id: UserId,
        auth_token: str,
        conn: WebSocketClientProtocol,
        activity_interval: float,
        autoread: bool,
        activity_auto_start: bool = True,
    ) -> None:
        super().__init__(logger=logger, conn=conn)
        self.user_id = user_id
        self.chat_id: int | None = None
        self._activity_auto_start = activity_auto_start
        self._activity_interval = activity_interval
        self._auth_token = auth_token
        self._activity_loop_task: asyncio.Task[Any] | None = None
        self._main_loop_task: asyncio.Task[Any] | None = None
        self._last_msg_sent = datetime_now()
        self._autoread = autoread

    async def __aenter__(self) -> "InteractiveChatClient":
        self.start()
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self.stop()

    def start(self) -> None:
        self._main_loop_task = asyncio.create_task(self._main_loop())
        self._show_help()

    async def stop(self) -> None:
        await self.stop_activity()

    async def stop_activity(self) -> None:
        if self._activity_loop_task:
            self.logger.debug("Activity stopped")
            self._activity_loop_task.cancel()
            await self._activity_loop_task
            self._activity_loop_task = None

    async def handle(self, command: str) -> None:
        match command.split():
            case ["/t"]:
                await self._send_is_typing()

            case ["/online"]:
                if not self._activity_loop_task:
                    self._activity_loop_task = asyncio.create_task(self._activity_loop())

            case ["/offline"]:
                if self._activity_loop_task:
                    await self.stop_activity()

            case ["/chats"]:
                await self._show_chats()

            case ["/chat", chat_id]:
                self.chat_id = int(chat_id)
                print(f"$ Chat switched to {chat_id}")

            case ["/chat", chat_id, "show"]:
                await self._show_chat(int(chat_id))

            case ["/read", message_id]:
                await self.send_message_received(int(message_id))
                await self.send_message_read(int(message_id))

            case ["/matches"]:
                await self._show_matches()

            case ["/msgs", chat_id, from_id, count]:
                await self._show_messages_in_chat(chat_id=int(chat_id), from_id=int(from_id), count=int(count))

            case ["/unread"]:
                await self._show_unread_count()

            case ["/exitchat"]:
                self.chat_id = None
                print("$ Exited chat")

            case ["/help"]:
                self._show_help()

            case _:
                if not self.chat_id:
                    print("$ You are not in the chat room, enter chat room with cmd '/chat <chat_id>'")
                    return

                await self.send_text_message(command, chat_id=self.chat_id)
                self._last_msg_sent = datetime_now()

    async def _send_is_typing(self) -> None:
        if not self.chat_id:
            print("$ You are not in the chat room, enter chat room with cmd '/chat <chat_id>'")
            return

        await self.send_activity(chat_id=self.chat_id, is_typing=True)

    async def _show_messages_in_chat(self, chat_id: int, from_id: int, count: int) -> None:
        async with AsyncClient() as client:
            result = await client.get(
                f"http://{self.conn._host}:{self.conn._port}/api/v1/chats/{chat_id}/messages",
                params={
                    "from_message_id": from_id,
                    "limit": count,
                },
                headers={"Authorization": f"Bearer {self._auth_token}"},
            )
            resp_json = result.json()
            print(f"$ Messages in chat {chat_id}:")
            for msg_data in resp_json:
                print(f"> User#{msg_data['sender_id']:<3} (msg#{msg_data['id']:>7}): {msg_data['content']}")

    async def _show_unread_count(self) -> None:
        async with AsyncClient() as client:
            result = await client.get(
                f"http://{self.conn._host}:{self.conn._port}/api/v1/chats/unread_count",
                headers={"Authorization": f"Bearer {self._auth_token}"},
            )
            resp_json = result.json()
            print(f"~~~ Total unread count: {resp_json['unread']}")

    async def _show_chat(self, chat_id: int) -> None:
        async with AsyncClient() as client:
            result = await client.get(
                f"http://{self.conn._host}:{self.conn._port}/api/v1/chats/{chat_id}",
                headers={"Authorization": f"Bearer {self._auth_token}"},
            )
            resp_json = result.json()
            print(f"~~~ Chat #{chat_id}: ~~~")
            print(resp_json)

    async def _show_matches(self) -> None:
        async with AsyncClient() as client:
            result = await client.get(
                f"http://{self.conn._host}:{self.conn._port}/api/v1/matches",
                headers={"Authorization": f"Bearer {self._auth_token}"},
            )
            resp_json = result.json()
            print("~~~ Match list: ~~~")
            for match_data in resp_json:
                print(f"Match #{match_data}")

            print("~~~ End match list: ~~~")

    async def _show_chats(self) -> None:
        async with AsyncClient() as client:
            result = await client.get(
                f"http://{self.conn._host}:{self.conn._port}/api/v1/chats",
                headers={"Authorization": f"Bearer {self._auth_token}"},
                params={"match_id": 1},
            )
            resp_json = result.json()
            print("~~~ Chat list: ~~~")
            print(resp_json)
            for chat_data in resp_json:
                print(f"Chat #{chat_data}")

            print("~~~ End chat list: ~~~")

    def _show_help(self) -> None:
        print(
            """
            Commands:
            /help - show this message
            /online - go online
            /offline - go offline
            /chat <chat_id> - enter chat room
            /chat <chat_id> show - show chat info
            /exitchat - exit chat room
            /chats - show all chats
            /msgs <chat_id> <from_id> <count> - retrieve last N messages from chat
            /t - imitate *typing in chat* behaviour
            /read <message_id> - mark the message as read and received
            /matches - list all matches (first page)
            /unread - show unread count for all chats
            *anytext* - Send message to the current chat
        """,
        )

    async def _main_loop(self) -> None:
        if self._activity_auto_start:
            self.logger.debug("Activity started")
            self._activity_loop_task = asyncio.create_task(self._activity_loop())

        while True:
            try:
                msg = await self.receive_message()
                handlers: dict[Type[ProtobufMessage], AnyHandler] = {
                    DeliveryStatusChangedUpdate: self._on_msg_status_updated,
                    MessageReceivedUpdate: self._on_new_message_received,
                    MessageSentUpdate: self._on_message_sent,
                    UserStatusChangedUpdate: self._on_presence_status_changed,
                    UserIsTypingUpdate: self._on_user_is_typing,
                }
                if handler := handlers.get(type(msg), None):
                    await handler(msg)

            except (asyncio.CancelledError, KeyboardInterrupt, ConnectionClosed):
                return

            except Exception as exc:  # pylint: disable=broad-except
                self.logger.exception(f"Error in interactive client: {exc}", exc_info=True)
                raise exc

    async def _activity_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(self._activity_interval)

                await self.send_activity(chat_id=self.chat_id, is_typing=False)

            except asyncio.CancelledError:
                return

    async def _on_msg_status_updated(self, update: DeliveryStatusChangedUpdate) -> None:
        rtt = round((datetime_now() - self._last_msg_sent).total_seconds(), 3)
        print(
            f"$ Msg#{update.message_id} / Chat#{update.chat_id}: {render_msg_status(update.state)} "
            f"(by User#{update.read_by}) (count: {update.updated_count:>3}) [RTT {rtt}]",
        )

    async def _on_new_message_received(self, update: MessageReceivedUpdate) -> None:
        msg = update.message
        is_message_from_self = msg.sender_id == self.user_id

        user_label = f"User#{msg.sender_id}" if not is_message_from_self else "Me"
        print(f"> {user_label:<8} (msg#{update.message.id:>7}): {extract_text_content(msg.content)}")

        if not is_message_from_self and update.message.chat_id == self.chat_id and self._autoread:
            await self.send_message_received(msg.id)
            await self.send_message_read(msg.id)

    async def _on_message_sent(self, update: MessageSentUpdate) -> None:
        rtt = round((datetime_now() - self._last_msg_sent).total_seconds(), 3)
        print(f"^ Sent: id#{update.message_id} [RTT {rtt}]")

    async def _on_presence_status_changed(self, update: UserStatusChangedUpdate) -> None:
        status = "online" if update.status == UserStatus.USER_STATUS_ONLINE else "offline"
        print(f"$ User#{update.user_id} is {status}")

    async def _on_user_is_typing(self, update: UserIsTypingUpdate) -> None:
        print(f"$ User#{update.user_id} is typing ...")
