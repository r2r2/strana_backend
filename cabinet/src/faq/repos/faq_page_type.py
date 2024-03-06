from tortoise import Model, fields

from common.orm.mixins import ListMixin, CreateMixin
from src.faq.entities import BaseFAQRepo


class FAQPageType(Model):
    """Тип страниц для вывода FAQ"""
    slug: str = fields.CharField(description="Слаг", max_length=250, pk=True)
    title: str = fields.CharField(description="Название", max_length=250)

    def __str__(self) -> str:
        return self.slug

    class Meta:
        table = "faq_faqpagetype"


class FAQPageTypeRepo(BaseFAQRepo, ListMixin, CreateMixin):
    """Репозиторий Типов страниц для вывода FAQ"""

    model = FAQPageType
