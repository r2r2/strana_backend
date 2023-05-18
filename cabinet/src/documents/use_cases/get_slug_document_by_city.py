from typing import Any, Type

from ..entities import BaseDocumentCase
from ..exceptions import DocumentNotFoundError
from ..repos import Document, DocumentRepo


class GetSlugDocumentByCityCase(BaseDocumentCase):
    """
    Получение оферты онлайн-покупки в зависимости от города
    """

    def __init__(self, document_repo: Type[DocumentRepo]) -> None:
        self.document_repo: DocumentRepo = document_repo()

    async def __call__(self, document_slug: str, city_slug: str) -> Document:
        filters: dict[str, Any] = dict(slug=f"{document_slug}__{city_slug}")
        document: Document = await self.document_repo.retrieve(filters=filters)
        if not document:
            raise DocumentNotFoundError
        return document
