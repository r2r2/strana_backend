from datetime import datetime
from typing import Optional

from tortoise import fields

from common import orm
from common.orm.mixins import CRUDMixin

from ..entities import BaseNewsDatabaseModel, BaseNewsRepo


class NewsViewedInfo(BaseNewsDatabaseModel):
    """
    Просмотренные новости.
    """

    id: int = fields.IntField(description="ID", pk=True, index=True)
    news: Optional[fields.ForeignKeyNullableRelation["News"]] = fields.ForeignKeyField(
        description="Новость",
        model_name="models.News",
        related_name="news_viewed_info",
        on_delete=fields.SET_NULL,
        null=True,
    )
    user: fields.ForeignKeyNullableRelation["User"] = fields.ForeignKeyField(
        description="Пользователь",
        model_name="models.User",
        related_name="news_viewed_info",
        null=True,
    )
    viewing_date: Optional[datetime] = fields.DatetimeField(
        auto_now_add=True,
        description="Дата и время просмотра",
        null=True,
    )
    is_voice_left: bool = fields.BooleanField(description="Пользователь проголосовал под новостью", default=False)
    is_useful: bool = fields.BooleanField(description="Новость была полезной", default=False)

    def __repr__(self):
        return f"Инфо о просмотре, id - {self.id}"

    class Meta:
        table = "news_news_viewed_info"


class NewsViewedInfoRepo(BaseNewsRepo, CRUDMixin):
    """
    Репозиторий просмотренных новостей.
    """

    model = NewsViewedInfo
    q_builder: orm.QBuilder = orm.QBuilder(NewsViewedInfo)
    c_builder: orm.ConverterBuilder = orm.ConverterBuilder(NewsViewedInfo)
    a_builder: orm.AnnotationBuilder = orm.AnnotationBuilder(NewsViewedInfo)
