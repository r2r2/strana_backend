from typing import Any, Type

from ..entities import BaseDocumentCase
from ..exceptions import EscrowNotFoundError
from ..repos import Escrow, EscrowRepo


class GetSlugEscrowCase(BaseDocumentCase):
    """
    Получение памятки эскроу
    """

    def __init__(self, escrow_repo: Type[EscrowRepo]) -> None:
        self.escrow_repo: EscrowRepo = escrow_repo()

    async def __call__(self, escrow_slug: str) -> Escrow:
        filters: dict[str, Any] = dict(slug=escrow_slug)
        escrow_document: Escrow = await self.escrow_repo.retrieve(filters=filters)
        if not escrow_document:
            raise EscrowNotFoundError
        return escrow_document
