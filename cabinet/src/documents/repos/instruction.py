from typing import Any, Optional

from tortoise import Model, fields
from common import cfields
from common.orm.mixins import ReadWriteMixin

from ..entities import BaseDocumentRepo


class Instruction(Model):
    """
    Инструкция
    """

    id: int = fields.IntField(description="ID", pk=True)
    slug: str = fields.CharField(description="Слаг", max_length=50)
    link_text: str = fields.TextField(description="Текст ссылки")
    file: Optional[dict[str, Any]] = cfields.MediaField(
        description="Файл", max_length=300, null=True
    )

    class Meta:
        table = "documents_instruction"


class InstructionRepo(BaseDocumentRepo, ReadWriteMixin):
    """
    Репозиторий инструкций
    """
    model = Instruction
