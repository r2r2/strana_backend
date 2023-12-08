from typing import Optional, Any

from tortoise import fields

from common import cfields
from common.orm.mixins import ReadOnlyMixin

from ..entities import BaseNewsDatabaseModel, BaseNewsRepo


class NewsSettings(BaseNewsDatabaseModel):
    """
    Настройки новостей.
    """

    id: int = fields.BigIntField(description="ID", pk=True, index=True)
    default_image_preview: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение (превью) по умолчанию",
        max_length=500,
    )
    default_image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение по умолчанию",
        max_length=500,
    )

    def __repr__(self):
        return "Настройки новостей"

    class Meta:
        table = "news_news_settings"


class NewsSettingsRepo(BaseNewsRepo, ReadOnlyMixin):
    """
    Репозиторий настрек новостей.
    """

    model = NewsSettings
