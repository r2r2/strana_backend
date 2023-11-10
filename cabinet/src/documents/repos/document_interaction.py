from typing import Any, Optional
from common import cfields

from tortoise import Model, fields
from common.orm.mixins import ReadWriteMixin, GenericMixin, CountMixin
from common import orm

from ..entities import BaseDocumentRepo


class InteractionDocument(Model):
    """
    Взаимодейтвие
    """
    
    id: int = fields.IntField(description="ID", pk=True)
    name: str = fields.CharField(max_length=150, description="Имя взаимодействия")
    icon: Optional[str] = cfields.MediaField(
        description="Иконка", max_length=350, null=True
    )
    file: Optional[dict[str, Any]] = cfields.MediaField(
        description="Файл", max_length=300, null=True,
    )
    priority = fields.IntField(description="Приоритет взаимодействия")

    class Meta:
        table = "documents_interaction"
        ordering = ["priority"]


class InteractionDocumentRepo(BaseDocumentRepo, GenericMixin, CountMixin):
    """
    Репозиторий взаимодействий
    """
    model = InteractionDocument
    q_builder: orm.QBuilder = orm.QBuilder(InteractionDocument)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(InteractionDocument)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(InteractionDocument)
