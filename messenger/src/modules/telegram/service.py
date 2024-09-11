import asyncio
from typing import Any

from aiogram import Bot

from src.core.logger import LoggerName, get_logger

from .entities import NewTicketTgNotificationPayload
from .interface import SupportedMessages, TelegramServiceProto
from .renderer import TelegramMessageRenderer
from .sender import TelegramSender
from .settings import TelegramServiceSettings


class TelegramService(TelegramServiceProto):
    def __init__(
        self,
        settings: TelegramServiceSettings,
    ) -> None:
        self._settings = settings
        self._bot = Bot(token=settings.api_token.get_secret_value())
        self._read_messages_task: asyncio.Task[Any] | None = None
        self.__messages_queue: asyncio.Queue[SupportedMessages] | None = None

        self.logger = get_logger(LoggerName.TELEGRAM)
        self.sender = TelegramSender(self._bot)
        self.renderer = TelegramMessageRenderer(url_templates=settings.url_templates)

    async def start(self) -> None:
        self.__messages_queue = asyncio.Queue()
        self._read_messages_task = asyncio.create_task(self._process_messages())

    async def stop(self) -> None:
        if self._read_messages_task:
            self._read_messages_task.cancel()
            await self._read_messages_task

    def send_message(self, message: SupportedMessages) -> None:
        if self.__messages_queue:
            self.logger.debug(f"Добавили сообщение в очередь: {message}")
            self.__messages_queue.put_nowait(message)

    async def _send_new_ticket_notification(self, payload: NewTicketTgNotificationPayload) -> None:
        await self.sender.send_message(
            chat_id=self._settings.notifications_channel_id,
            text=self.renderer.render_new_ticket_notification_text(payload),
            escape_markdown=False,
        )

    async def _process_messages(self) -> None:
        while self.__messages_queue:
            try:
                message = await self.__messages_queue.get()
                self.logger.debug(f"Обрабатываем сообщение из очереди: {message}")

                handlers = {
                    NewTicketTgNotificationPayload: self._send_new_ticket_notification,
                }

                handler = handlers.get(type(message), None)
                if not handler:
                    raise NotImplementedError(f"Неизвестный тип сообщения: {type(message)}")

                await handler(message)

            except asyncio.CancelledError:
                self.logger.debug("Отправка сообщений отменена")
                break

            except Exception as exc:
                self.logger.error(
                    f"Ошибка при отправке сообщения: {type(exc)}: {exc}",
                    extra={"exc": exc, "queue_size": self.__messages_queue.qsize() if self.__messages_queue else 0},
                    exc_info=True,
                )
