from tortoise import fields

from common import orm
from common.orm.mixins import CRUDMixin

from ..entities import BaseNewsDatabaseModel, BaseNewsRepo


class NewsTag(BaseNewsDatabaseModel):
    """
    Теги новостей.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    label: str = fields.CharField(
        description="Название тега",
        max_length=100,
    )
    slug: str = fields.CharField(
        description="Слаг тега",
        max_length=100,
        unique=True,
    )
    is_active: bool = fields.BooleanField(description="Активность", default=True)
    priority: int = fields.IntField(description="Приоритет", default=0)

    def __repr__(self):
        return self.label

    class Meta:
        table = "news_news_tag"


class NewsTagRepo(BaseNewsRepo, CRUDMixin):
    """
    Репозиторий тегов новостей.
    """

    model = NewsTag
    q_builder: orm.QBuilder = orm.QBuilder(NewsTag)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(NewsTag)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(NewsTag)
