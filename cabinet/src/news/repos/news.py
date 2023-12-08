from typing import Optional, Any
from datetime import datetime

from tortoise import fields

from common import cfields, orm
from common.orm.mixins import CRUDMixin, CountMixin

from ..entities import BaseNewsDatabaseModel, BaseNewsRepo


class News(BaseNewsDatabaseModel):
    """
    Новости.
    """

    id: int = fields.BigIntField(description="ID", pk=True, index=True)
    title: str = fields.CharField(
        description="Заголовок новости",
        max_length=150,
    )
    slug: str = fields.CharField(
        description="Слаг новости",
        max_length=100,
        unique=True,
    )
    short_description: Optional[str] = fields.TextField(
        description="Краткое описание новости",
        null=True,
    )
    description: Optional[str] = fields.TextField(
        description="Описание новости",
        null=True,
    )
    is_active: bool = fields.BooleanField(
        description="Новость активна",
        default=True,
    )
    image_preview: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение (превью)", max_length=500, null=True,
    )
    image: Optional[dict[str, Any]] = cfields.MediaField(
        description="Изображение", max_length=500, null=True,
    )
    pub_date: Optional[datetime] = fields.DatetimeField(
        description="Дата публикации новости",
        null=True,
    )
    end_date: Optional[datetime] = fields.DatetimeField(
        description="Дата окончания новости",
        null=True,
    )

    tags: fields.ManyToManyRelation["NewsTag"] = fields.ManyToManyField(
        description="Теги",
        model_name='models.NewsTag',
        through="news_news_tag_through",
        backward_key="news_id",
        forward_key="news_tag_id",
        related_name="news",
    )
    roles: fields.ManyToManyRelation["UserRole"] = fields.ManyToManyField(
        description="Роли",
        model_name='models.UserRole',
        through="news_news_user_role_through",
        backward_key="news_id",
        forward_key="role_id",
        related_name="news",
    )
    news_projects: fields.ManyToManyRelation["Project"] = fields.ManyToManyField(
        description="Проекты",
        model_name='models.Project',
        through="news_news_project_through",
        backward_key="news_id",
        forward_key="project_id",
        related_name="news",
    )

    created_at: datetime = fields.DatetimeField(description="Время создания", auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(description="Время обновления", auto_now=True)

    def __repr__(self):
        return self.title

    class Meta:
        table = "news_news"


class NewsNewsTagThrough(BaseNewsDatabaseModel):
    """
    Выбранные теги для новостей.
    """

    news: fields.ForeignKeyRelation[News] = fields.ForeignKeyField(
        model_name="models.News",
        related_name="news_tag_through",
        description="Новость",
        on_delete=fields.CASCADE,
    )
    news_tag: fields.ForeignKeyRelation["NewsTag"] = fields.ForeignKeyField(
        model_name="models.NewsTag",
        related_name="news_through",
        description="Тег",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "news_news_tag_through"


class NewsUserRoleThrough(BaseNewsDatabaseModel):
    """
    Выбранные роли пользователей для новостей.
    """

    news: fields.ForeignKeyRelation[News] = fields.ForeignKeyField(
        model_name="models.News",
        related_name="user_role_through",
        description="Новость",
        on_delete=fields.CASCADE,
    )
    role: fields.ForeignKeyRelation["UserRole"] = fields.ForeignKeyField(
        model_name="models.UserRole",
        related_name="news_through",
        description="Роль пользователя",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "news_news_user_role_through"


class NewsProjectThrough(BaseNewsDatabaseModel):
    """
    Выбранные проекты для новостей.
    """

    news: fields.ForeignKeyRelation[News] = fields.ForeignKeyField(
        model_name="models.News",
        related_name="project_through",
        description="Новость",
        on_delete=fields.CASCADE,
    )
    project: fields.ForeignKeyRelation["Project"] = fields.ForeignKeyField(
        model_name="models.Project",
        related_name="news_through",
        description="Проект",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "news_news_project_through"
        ordering = ["pub_date"]


class NewsRepo(BaseNewsRepo, CRUDMixin, CountMixin):
    """
    Репозиторий новостей.
    """

    model = News
    q_builder: orm.QBuilder = orm.QBuilder(News)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(News)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(News)
