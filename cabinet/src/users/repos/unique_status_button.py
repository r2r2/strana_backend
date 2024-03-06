from tortoise import Model, fields

from common.orm.mixins import CRUDMixin
from src.users.entities import BaseUserRepo


class UniqueStatusButton(Model):
    """
    Кнопка статуса уникальности
    """
    id: int = fields.IntField(description="ID", pk=True)
    text: str = fields.CharField(max_length=255, description="Текст", null=True)
    slug: str = fields.CharField(max_length=255, description="Слаг", null=True)
    background_color: str = fields.CharField(default="#8F00FF", description="Цвет фона", max_length=7, null=True)
    text_color: str = fields.CharField(default="#FFFFFF", description="Цвет текста", max_length=7, null=True)
    description: str = fields.TextField(description="Описание", null=True)

    terms: fields.ReverseRelation["CheckTerm"]

    class Meta:
        table = "users_unique_statuses_buttons"


class UniqueStatusButtonRepo(BaseUserRepo, CRUDMixin):
    """
    Репозиторий кнопок статусов уникальности
    """
    model = UniqueStatusButton
