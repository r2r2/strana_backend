import asyncio
import logging

from aiogram import Bot

from sl_telegram_notifier.config import TelegramNotifierConfig


class TelegramNotifier:
    def __init__(
        self,
        config: TelegramNotifierConfig,
        logger: logging.Logger = logging.getLogger(),
    ) -> None:
        self._config = config
        self._bot = Bot(token=self._config.token.get_secret_value())
        self._logger = logger
        self._read_messages_task: asyncio.Task | None = None
        self.__messages_queue: asyncio.Queue | None = None

    async def start(self) -> None:
        self.__messages_queue = asyncio.Queue()
        self._read_messages_task = asyncio.create_task(self._process_messages())

    async def stop(self) -> None:
        if self._read_messages_task:
            self._read_messages_task.cancel()
            await self._read_messages_task
        await self._bot.session.close()

    def send_message(self, message: str) -> None:
        if self.__messages_queue:
            self._logger.debug("Добавили сообщение в очередь: %s", message)
            self.__messages_queue.put_nowait(message)

    async def _send_telegram_message(self, message: str, parse_mode: str = "Markdown") -> None:
        if self._config.is_enabled:
            await self._bot.send_message(
                chat_id=self._config.chat_id,
                text=message,
                parse_mode=parse_mode,
            )

    async def _process_messages(self) -> None:
        while self.__messages_queue:
            try:
                message = await self.__messages_queue.get()
                self._logger.debug("Обрабатываем сообщение из очереди: %s", message)
                await self._send_telegram_message(message)

            except asyncio.CancelledError:
                self._logger.debug("Отправка сообщений отменена")
                break

            except Exception as exc:
                self._logger.debug(
                    "Ошибка при отправке сообщения",
                    extra={"exc": exc, "queue_size": self.__messages_queue.qsize() if self.__messages_queue else 0},
                    exc_info=True,
                )
