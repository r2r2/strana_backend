from typing import Optional, Any
from tortoise import Model, fields
from common import cfields, orm
from common.orm.mixins import ListMixin, CRUDMixin, CountMixin

from ..entities import BaseSliderRepo


class Slider(Model):
    """
    Модель слайдера авторизации
    """

    is_active: bool = fields.BooleanField(description="Активность", default=True)

    priority: int = fields.IntField(default=0, description='Приоритет')

    title: Optional[str] = fields.CharField(
        description="Заголовок слайда", max_length=300, null=True
    )

    subtitle: Optional[str] = fields.CharField(
        description="Подзаголовок слайда", max_length=300, null=True
    )

    desktop_media: Optional[dict[str, Any]] = cfields.MediaField(
        description="Картинка/видео для десктопа", max_length=300, null=True,
    )

    tablet_media: Optional[dict[str, Any]] = cfields.MediaField(
        description="Картинка/видео для планшета", max_length=300, null=True,
    )

    mobile_media: Optional[dict[str, Any]] = cfields.MediaField(
        description="Картинка/видео для мобильной версии", max_length=300, null=True,
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        table = "slider_auth"
        ordering = ["priority"]

class SliderRepo(BaseSliderRepo, CRUDMixin, ListMixin, CountMixin):
    """
    Репозиторий слайдера авторизации
    """
    model = Slider
    