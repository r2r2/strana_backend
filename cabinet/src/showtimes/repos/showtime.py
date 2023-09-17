from datetime import datetime
from typing import Optional, Any, Union

from tortoise import Model, fields
from tortoise.fields import ForeignKeyNullableRelation
from tortoise.expressions import Q
from tortoise.queryset import QuerySet, QuerySetSingle

from common import cfields
from common.orm.mixins import ReadWriteMixin

from src.users.repos import User
from src.projects.repos import Project
from src.properties.constants import PropertyTypes

from ..entities import BaseShowTimeRepo


class ShowTime(Model):
    """
    Запись на показ
    """

    id: int = fields.BigIntField(description="ID", pk=True)
    visit: datetime = fields.DatetimeField(description="Дата и время посещения", null=True)
    property_type: Optional[str] = cfields.CharChoiceField(
        description="Тип недвижимости", max_length=50, null=True, choice_class=PropertyTypes
    )
    project: ForeignKeyNullableRelation[Project] = fields.ForeignKeyField(
        description="Проект",
        model_name="models.Project",
        on_delete=fields.SET_NULL,
        related_name="showtimes",
        null=True
    )
    user: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Пользователь",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="showtimes",
        null=True,
    )
    agent: ForeignKeyNullableRelation[User] = fields.ForeignKeyField(
        description="Агент",
        model_name="models.User",
        on_delete=fields.SET_NULL,
        related_name="registered_showtimes",
        null=True,
    )
    amocrm_id: Optional[int] = fields.BigIntField(description="AmoCRM ID", null=True)

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        table = "showtimes_showtime"


class ShowTimeRepo(BaseShowTimeRepo, ReadWriteMixin):
    """
    Репозиторий записи на показ
    """
    model = ShowTime

    def retrieve(
        self,
        filters: dict[str, Any],
        q_filters: Optional[list[Q]] = None,
        annotations: Optional[list[Any]] = None,
        related_fields: Optional[list[str]] = None,
        prefetch_fields: Optional[list[Union[str, dict[str, Any]]]] = None,
        order_by: Optional[str] = None,
    ) -> QuerySetSingle[ShowTime]:
        """
        Получение записи на показ
        todo: Что за мазафака, почему это закомичено?
        """
        showtime: QuerySet[ShowTime] = ShowTime.filter(**filters)
        # if q_filters:
        #     showtime: QuerySet[ShowTime] = showtime.filter(*q_filters)
        if related_fields:
            showtime: QuerySet[ShowTime] = showtime.select_related(*related_fields)
        # if prefetch_fields:
        #     prefetches: list[Union[str, Prefetch]] = list()
        #     for prefetch in prefetch_fields:
        #         if isinstance(prefetch, str):
        #             prefetches.append(prefetch)
        #         else:
        #             prefetches.append(Prefetch(**prefetch))
        #     showtime: QuerySet[ShowTime] = showtime.prefetch_related(*prefetches)
        # if annotations:
        #     showtime: QuerySet[ShowTime] = showtime.annotate(**annotations)
        showtime: QuerySetSingle[ShowTime] = showtime.first()
        return showtime
