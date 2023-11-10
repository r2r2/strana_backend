from typing import Any, Optional

from tortoise import Model, fields

from common import cfields
from common.orm.mixins import CRUDMixin

from ..entities import BaseNotificationRepo


class TemplateContent(Model):
    """
    Контент шаблонов писем.
    """

    id: int = fields.IntField(description="ID", pk=True)
    description: str = fields.TextField(description="Описание")
    slug: str = fields.CharField(max_length=50, description="Слаг", null=True)
    file: Optional[dict[str, Any]] = cfields.MediaField(description="Файл", max_length=300, null=True)

    class Meta:
        table = "notifications_template_content"


class TemplateContentRepo(BaseNotificationRepo, CRUDMixin):
    """
    Репозиторий контента шаблонов писем.
    """
    model = TemplateContent
