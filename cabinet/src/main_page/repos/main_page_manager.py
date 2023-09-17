from typing import Annotated, Optional

from common import cfields
from common.orm.entities import BaseRepo
from common.orm.mixins import ListMixin, RetrieveMixin
from pydantic import Field
from tortoise import Model, fields


class MainPageManager(Model):
    """
    Блок: Менеджер на главной
    """
    id: int = fields.IntField(description="ID", pk=True)
    manager = fields.ForeignKeyField(
        'models.Manager',
        related_name='main_page',
        on_delete=fields.CASCADE,
        description='Менеджер'
    )
    position: Optional[str] = fields.CharField(description='Должность', null=True, max_length=512)
    photo: Annotated[str, Field(max_length=2000)] = cfields.MediaField(
        description="Фото", max_length=2000, null=True
    )

    class Meta:
        table = "main_page_manager"


class MainPageManagerRepo(BaseRepo, RetrieveMixin, ListMixin):
    """
    Репозиторий менеджера главной страницы
    """
    model = MainPageManager
