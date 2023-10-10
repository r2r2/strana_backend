from common.models import TimeBasedMixin
from common.orm.entities import BaseRepo
from common.orm.mixins import ReadWriteMixin
from tortoise import Model, fields


class MainPageText(Model, TimeBasedMixin):
    """
    Контент и заголовки главной страницы
    """
    id: int = fields.IntField(description="ID", pk=True)
    title: str = fields.TextField(
        max_length=255,
        description="Заголовок блока",
        null=True,
    )
    text: str = fields.TextField(description="Текст главной страницы", null=True)
    slug: str = fields.CharField(max_length=50, description='Slug', unique=True)
    comment: str = fields.TextField(
        max_length=255,
        description="Внутренний комментарий",
        null=True,
    )

    class Meta:
        table = "main_page_content"


class MainPageTextRepo(BaseRepo, ReadWriteMixin):
    """
    Репозиторий Контента и заголовков главной страницы
    """
    model = MainPageText
