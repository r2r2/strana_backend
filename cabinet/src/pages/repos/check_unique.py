from common import cfields
from typing import Optional, Any
from tortoise import Model, fields

from common.orm.mixins import RetrieveMixin, CreateMixin
from ..entities import BasePageRepo


class CheckUnique(Model):
    """
    Проверка на уникальность
    """

    id: int = fields.IntField(description="ID", pk=True)
    check_image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение проверка", max_length=500, null=True
    )
    result_image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение результат", max_length=500, null=True
    )

    def __str__(self) -> str:
        return self.__doc__.strip()

    class Meta:
        table = "pages_check_unique"


class CheckUniqueRepo(BasePageRepo, CreateMixin, RetrieveMixin):
    """
    Репозиторий проверки на уникальность
    """
    model = CheckUnique
