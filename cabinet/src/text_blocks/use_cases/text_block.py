from typing import Any, Type

from src.text_blocks.repos import TextBlock, TextBlockRepo

from ..entities import BaseTextBlockCase
from ..exceptions import TextBlockNotFoundError
from ..services import TextBlockHandlerService


class TextBlockCase(BaseTextBlockCase):
    """
    Кейс для получения общих текстовых блоков по слагу.
    """

    def __init__(
        self,
        text_block_repo: Type[TextBlockRepo],
        handlers_service: TextBlockHandlerService,
    ) -> None:
        self.text_block_repo: TextBlockRepo = text_block_repo()
        self.handlers_service: TextBlockHandlerService = handlers_service

    async def __call__(
        self,
        slug: str,
        **kwargs,
    ) -> Any:
        text_block: TextBlock = await self.text_block_repo.retrieve(filters=dict(slug=slug))
        if not text_block:
            raise TextBlockNotFoundError

        modify_text_block = await self.handlers_service(slug=slug, text_block=text_block, **kwargs)
        if modify_text_block:
            return modify_text_block
        else:
            return text_block
