from common.orm.entities import BaseRepo
from common.orm.mixins import RetrieveMixin
from tortoise import Model, fields


class MainPageManager(Model):
    """
    Блок: Продавайте online
    """
    id: int = fields.IntField(description="ID", pk=True)
    manager = fields.ForeignKeyField(
        'models.Manager',
        related_name='main_page',
        on_delete=fields.CASCADE,
        description='Менеджер'
    )

    class Meta:
        table = "main_page_manager"


class MainPageManagerRepo(BaseRepo, RetrieveMixin):
    """
    Репозиторий менеджера главной страницы
    """
    model = MainPageManager
