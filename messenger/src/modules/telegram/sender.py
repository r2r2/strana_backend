from aiogram import Bot
from aiogram import types as tgtypes

from .helpers import escape_markdown_v2, throttled


class TelegramSender:
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    @throttled(rps=1)
    async def send_message(
        self,
        chat_id: int,
        text: str,
        escape_markdown: bool = False,
        reply_to_message_id: int | None = None,
    ) -> tgtypes.Message:
        """Send message via the telegram bot api. Api is ratelimited (1 message per second per chat)"""
        return await self._bot.send_message(
            chat_id=chat_id,
            parse_mode="MarkdownV2",
            text=escape_markdown_v2(text) if escape_markdown else text,
            reply_to_message_id=reply_to_message_id,
        )
