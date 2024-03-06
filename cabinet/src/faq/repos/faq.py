from typing import Optional

from tortoise import Model, fields

from common.orm.mixins import ListMixin, CreateMixin
from src.faq.entities import BaseFAQRepo


class FAQ(Model):
    id: int = fields.IntField(description="ID", pk=True)
    slug: Optional[str] = fields.CharField(description="Слаг", max_length=100, null=False)
    is_active: bool = fields.BooleanField(description="Активный", default=True)
    order: int = fields.IntField(description="Порядок", default=0)
    question: str = fields.CharField(description="Вопрос", max_length=100, null=False)
    answer: str = fields.TextField(description="Ответ")
    page_type = fields.ForeignKeyField(
        model_name="models.FAQPageType",
        on_delete=fields.SET_NULL,
        null=True,
        related_name="faq",
        description="Тип страницы",
    )

    def __str__(self) -> str:
        return f"{self.id}: {self.question}"

    class Meta:
        table = "faq_faq"
        ordering = ("order", )


class FAQRepo(BaseFAQRepo, ListMixin, CreateMixin):
    """Репозиторий FAQ"""

    model = FAQ

    async def get_active_faq_list(self, page_type: str | None = None) -> list[FAQ]:
        filters = dict(
            is_active=True
        )
        if page_type is not None:
            filters.update(page_type=page_type)

        return await self.list().filter(**filters)
