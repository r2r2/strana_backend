from typing import Any, Type

from ..entities import BaseDocumentCase
from ..exceptions import DocumentNotFoundError
from ..repos import Document, DocumentRepo


class GetSlugDocumentCase(BaseDocumentCase):
    """
    Получение документа по слагу
    """

    def __init__(self, document_repo: Type[DocumentRepo]) -> None:
        self.document_repo: DocumentRepo = document_repo()

    async def __call__(self, document_slug: str) -> Document:
        filters: dict[str, Any] = dict(slug=document_slug)
        document: Document = await self.document_repo.retrieve(filters=filters)
        if not document:
            raise DocumentNotFoundError
        return document
