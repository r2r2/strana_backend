"""
Model Mixins
"""

from typing import Any, Optional, Union

from tortoise import Model
from tortoise.expressions import F, Q
from tortoise.functions import Count, Max, Min
from tortoise.query_utils import Prefetch
from tortoise.queryset import (CountQuery, ExistsQuery, QuerySet,
                               QuerySetSingle, ValuesListQuery, ValuesQuery)


class BaseMixin:
    model: Model


class ExecuteMixin(BaseMixin):
    """
    Execute Raw SQL Mixin
    """
    async def execute(self, raw_sql) -> Any:
        return await self.model.raw(raw_sql)


class UpdateMixin(BaseMixin):
    """
    Update Mixin
    """
    async def update(self, model: 'UpdateMixin.model', data: dict[str, Any]) -> 'UpdateMixin.model':
        """
        Обновление модели
        """
        for field, value in data.items():
            setattr(model, field, value)
        await model.save()
        await model.refresh_from_db()
        return model


class BulkUpdateMixin(BaseMixin):
    """
    Bulk Update Mixin
    """
    async def bulk_update(
        self, data: dict[str, Any], filters: dict[str, Any], exclude_filters: dict[str, Any] = None
    ) -> None:
        """
        Обновление пачки бронирований
        """
        if not exclude_filters:
            qs: QuerySet[Model] = self.model.select_for_update().filter(**filters)
        else:
            qs: QuerySet[Model] = self.model.select_for_update().filter(**filters).exclude(**exclude_filters)
        await qs.update(**data)


class CreateMixin(BaseMixin):
    """
    Create Mixin
    """
    async def create(self, data: dict[str, Any]) -> 'CreateMixin.model':
        """
        Создание модели
        """
        model: 'CreateMixin.model' = await self.model.create(**data)
        return model


class DeleteMixin(BaseMixin):
    """
    Delete Mixin
    """
    async def delete(self, model: Model) -> None:
        """
        Удаление модели
        """
        await model.delete()


class UpdateOrCreateMixin(BaseMixin):
    """
    Update or create Mixin
    """
    async def update_or_create(
            self,
            filters: dict[str, Any],
            data: dict[str, Any]
    ) -> 'UpdateOrCreateMixin.model':
        """
        Создание или обновление модели
        """
        model, _ = await self.model.update_or_create(**filters, defaults=data)
        return model


class ExistsMixin(BaseMixin):
    """
    Exists Mixin
    """
    def exists(self, filters: dict[str, Any]) -> ExistsQuery:
        """
        Существование модели
        """
        models: ExistsQuery = self.model.filter(**filters).exists()
        return models


class RetrieveMixin(BaseMixin):
    """
    Retrieve Mixin
    """
    def retrieve(
        self,
        filters: dict[str, Any],
        q_filters: Optional[list[Q]] = None,
        annotations: Optional[dict[Any]] = None,
        related_fields: Optional[list[str]] = None,
        prefetch_fields: Optional[list[Union[str, dict[str, Any]]]] = None,
        ordering: Optional[str] = None,
    ) -> QuerySetSingle['RetrieveMixin.model']:
        """
        Получение модели
        """
        model: QuerySet[Model] = self.model.filter(**filters)
        if q_filters:
            model: QuerySet[Model] = model.filter(*q_filters)
        if related_fields:
            model: QuerySet[Model] = model.select_related(*related_fields)
        if prefetch_fields:
            prefetches: list[Union[str, Prefetch]] = []
            for prefetch in prefetch_fields:
                if isinstance(prefetch, str):
                    prefetches.append(prefetch)
                else:
                    prefetches.append(Prefetch(**prefetch))
            model: QuerySet[Model] = model.prefetch_related(*prefetches)
        if annotations:
            model: QuerySet[Model] = model.annotate(**annotations)
        if ordering:
            model: QuerySet[Model] = model.order_by(ordering)
        model: QuerySetSingle[Model] = model.first()
        return model


class ListMixin(BaseMixin):
    """
    List Mixin
    """
    def list(
        self,
        end: int | None = None,
        start: int | None = None,
        ordering: str | None = None,
        distinct: bool | None = False,
        q_filters: list[Q] | None = None,
        filters: dict[str, Any] | None = None,
        excluded: dict[str, Any] | None = None,
        related_fields: list[str] | None = None,
        annotations: dict[str, Any] | None = None,
        prefetch_fields: list[str | dict[str, Any]] | None = None,
    ) -> QuerySet['ListMixin.model']:
        """
        Получение списка моделей
        """
        models: QuerySet[Model] = self.model.all()
        if filters:
            models: QuerySet[Model] = models.filter(**filters)
        if excluded:
            models: QuerySet[Model] = models.exclude(**excluded)
        if q_filters:
            models: QuerySet[Model] = models.filter(*q_filters)
        if related_fields:
            models: QuerySet[Model] = models.select_related(*related_fields)
        if prefetch_fields:
            prefetches: list[str | Prefetch] = []
            for prefetch in prefetch_fields:
                if isinstance(prefetch, str):
                    prefetches.append(prefetch)
                else:
                    prefetches.append(Prefetch(**prefetch))
            models: QuerySet[Model] = models.prefetch_related(*prefetches)
        if annotations:
            models: QuerySet[Model] = models.annotate(**annotations)
        if start is not None and end is not None:
            models: QuerySet[Model] = models.offset(start).limit(end - start)
        if ordering:
            models: QuerySet[Model] = models.order_by(ordering)
        if distinct:
            models: QuerySet[Model] = models.distinct()
        return models


class CountMixin(BaseMixin):
    """
    Count Mixin
    todo: Отрефакторить, чтобы возвращался инт, а не список кортежей с одним элементом.
    """
    def count(
        self, filters: Optional[dict[str, Any]] = None, q_filters: Optional[list[Q]] = None
    ) -> ValuesListQuery:
        """
        Количество агентов
        """
        models: QuerySet[Model] = self.model.all()
        if filters:
            models: QuerySet[Model] = models.filter(**filters)
        if q_filters:
            models: QuerySet[Model] = models.filter(*q_filters)
        models: ValuesListQuery = models.annotate(count=Count("id", distinct=True)).values_list("count")
        return models


class SCountMixin(BaseMixin):
    """
    SCount Mixin
    """
    def scount(
            self,
            filters: Optional[dict[str, Any]] = None,
            q_filters: Optional[list[Q]] = None,
            distinct: Optional[bool] = True,
    ) -> CountQuery:
        """
        Количество агентов подзапросом
        """
        models: QuerySet[Model] = self.model.all()
        if filters:
            models: QuerySet[Model] = models.filter(**filters)
        if q_filters:
            models: QuerySet[Model] = models.filter(*q_filters)
        if distinct:
            models.distinct()
        models: CountQuery = models.count()
        return models


class SpecsMixin(BaseMixin):
    """
    Specs Mixin
    """
    def specs(
        self,
        field: str,
        filters: dict[str, Any],
        queryset: Union[QuerySet[Model], QuerySetSingle[Model]],
        group: Optional[str] = None,
        label: Optional[str] = None,
        ranges: Optional[bool] = False,
        choices: Optional[bool] = False,
    ) -> Union[ValuesListQuery, ValuesQuery]:
        """
        Спеки по полю
        """
        if choices:
            specs_queryset: ValuesListQuery = (
                queryset.filter(**filters).order_by(field).distinct().values_list(field, flat=True)
            )
        elif ranges:
            if group is None:
                group: str = "id"
            specs_queryset: ValuesQuery = (
                queryset.filter(**filters)
                .annotate(min=Min(field), max=Max(field))
                .group_by(group)
                .values(min=F("min"), max=F("max"))
            )
        else:
            specs_queryset: ValuesQuery = (
                queryset.filter(**filters)
                .order_by(field, label)
                .distinct()
                .values(value=field, label=label if label else field)
            )
        return specs_queryset


class FacetsMixin(BaseMixin):
    """
    Facets Mixin
    """
    def facets(
        self,
        field: str,
        filters: dict[str, Any],
        queryset: Union[QuerySet[Model], QuerySetSingle[Model]],
        group: Optional[str] = None,
        ranges: Optional[bool] = False,
    ) -> Union[ValuesListQuery, ValuesQuery]:
        """
        Фасеты по полю
        """
        if ranges:
            if group is None:
                group: str = "id"
            facets_queryset: ValuesQuery = (
                queryset.filter(**filters)
                .annotate(min=Min(field), max=Max(field))
                .group_by(group)
                .values(min=F("min"), max=F("max"))
            )
        else:
            facets_queryset: ValuesListQuery = (
                queryset.filter(**filters).order_by(field).distinct().values_list(field, flat=True)
            )
        return facets_queryset


class ReadOnlyMixin(ListMixin, RetrieveMixin, ExistsMixin):
    """Mixin for read-only repos"""


class WriteOnlyMixin(CreateMixin, UpdateMixin, UpdateOrCreateMixin, BulkUpdateMixin):
    """Mixin for write-only repos"""


class ReadWriteMixin(ReadOnlyMixin, WriteOnlyMixin):
    """Mixin for read and write repos"""


class CRUDMixin(ReadWriteMixin, DeleteMixin):
    """Create, update, retrieve, delete mixins"""


class GenericMixin(CRUDMixin, SpecsMixin, FacetsMixin, CountMixin, SCountMixin):
    """Generic mixin with all methods"""
