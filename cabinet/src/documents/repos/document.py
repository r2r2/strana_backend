from typing import Any, Optional

from tortoise import Model, fields

from common import cfields
from common.orm.mixins import ReadWriteMixin

from ..entities import BaseDocumentRepo


class Document(Model):
    """
    Документ
    """

    id: int = fields.IntField(description="ID", pk=True)
    text: str = fields.TextField(description="Текст")
    slug: str = fields.CharField(description="Слаг", max_length=50)
    file: Optional[dict[str, Any]] = cfields.MediaField(
        description="Файл", max_length=300, null=True
    )

    class Meta:
        table = "documents_document"


class DocumentRepo(BaseDocumentRepo, ReadWriteMixin):
    """
    Репозиторий документа
    """
    model = Document


class Escrow(Model):
    """
    Памятка эскроу
    """

    id: int = fields.IntField(description="ID", pk=True)
    slug: str = fields.CharField(description="Слаг", max_length=50)
    file: Optional[dict[str, Any]] = cfields.MediaField(
        description="Файл", max_length=300, null=True
    )

    class Meta:
        table = "documents_escrow"


class EscrowRepo(BaseDocumentRepo, ReadWriteMixin):
    """
    Репозиторий памятки эскроу
    """
    model = Escrow
