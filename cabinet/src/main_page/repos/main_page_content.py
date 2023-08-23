from common.models import TimeBasedMixin
from common.orm.entities import BaseRepo
from common.orm.mixins import ListMixin
from tortoise import Model, fields


class MainPageContent(Model, TimeBasedMixin):
    """
    Контент и заголовки главной страницы
    """
    id: int = fields.IntField(description="ID", pk=True)
    text: str = fields.TextField(description="Текст главной страницы")
    slug: str = fields.CharField(max_length=50, description='Slug')
    comment: str = fields.TextField(max_length=255, description="Внутренний комментарий")

    class Meta:
        table = "main_page_content"


class MainPageContentRepo(BaseRepo, ListMixin):
    """
    Репозиторий Контента и заголовков главной страницы
    """
    model = MainPageContent
