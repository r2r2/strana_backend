from datetime import datetime
from typing import Optional, Any

from tortoise import Model, fields

from common import cfields
from common.orm.mixins import ReadWriteMixin, ListMixin
from src.booking.entities import BaseDocumentArchiveRepo


class DocumentArchive(Model):
    """
    Архив документов (шаблонов оферт)
    """

    id: int = fields.IntField(description="ID", pk=True)
    offer_text: str = fields.TextField(description="Текст")
    slug: str = fields.CharField(description="Слаг", max_length=50)
    file: Optional[dict[str, Any]] = cfields.MediaField(
        description="Файл", max_length=300, null=True
    )
    date_time: datetime = fields.DatetimeField(
        description="Дата, время создания",
        auto_now_add=True
    )

    class Meta:
        table = "documents_document_archive"


class DocumentArchiveRepo(BaseDocumentArchiveRepo, ReadWriteMixin, ListMixin):
    """
    Репозиторий архива документов
    """

    model = DocumentArchive
